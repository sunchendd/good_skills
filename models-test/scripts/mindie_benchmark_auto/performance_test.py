# openai_api_test.py
# -*- coding: utf-8 -*-
import time
import json
import random
import requests
from concurrent.futures import ThreadPoolExecutor
from transformers import AutoTokenizer
import argparse 
import pandas as pd
from pathlib import Path
import numpy as np
from typing import Any, Union


class SampleRequest:
    """
    Represents a single inference request for benchmarking.
    """
    def __init__(self, prompt: Union[str, Any], prompt_len: int, expected_output_len: int):
        self.prompt = prompt
        self.prompt_len = prompt_len
        self.expected_output_len = expected_output_len


def save_to_csv(result, csv_file):
    df = pd.DataFrame(result)
    if Path(csv_file).exists():
        existing_df = pd.read_csv(csv_file)
        df = pd.concat([existing_df, df], ignore_index=True)
    
    df.to_csv(csv_file, index=False)


def sample_random_input(
    tokenizer,
    num_requests: int,
    prefix_len: int = 0,
    range_ratio: float = 1.0,
    input_len: int = 1024,
    output_len: int = 128):

    vocab_size = tokenizer.vocab_size

    prefix_token_ids = (np.random.randint(
        0, vocab_size, size=prefix_len).tolist() if prefix_len > 0 else [])

    input_low = int(input_len * range_ratio)
    output_low = int(output_len * range_ratio)

    input_lens = np.random.randint(input_low,
                                    input_len + 1,
                                    size=num_requests)
    output_lens = np.random.randint(output_low,
                                    output_len + 1,
                                    size=num_requests)
    offsets = np.random.randint(0, vocab_size, size=num_requests)

    requests = []
    for i in range(num_requests):
        inner_seq = ((offsets[i] + i + np.arange(input_lens[i])) %
                        vocab_size).tolist()
        token_sequence = prefix_token_ids + inner_seq
        prompt = tokenizer.decode(token_sequence)
        total_input_len = prefix_len + int(input_lens[i])
        requests.append(
            SampleRequest(
                prompt=prompt,
                prompt_len=total_input_len,
                expected_output_len=int(output_lens[i]),
            ))
    return requests


def sample_sonnet_input(
            dataset_path,
            tokenizer,
            num_requests: int,
            prefix_len: int = 0,
            input_len: int = 1024,
            output_len: int = 128,
            return_prompt_formatted: bool = False):
    # Calculate average token length for a poem line.
    with open(dataset_path, encoding="utf-8") as f:
        data = f.readlines()
    tokenized_lines = [tokenizer(line).input_ids for line in data]
    avg_len = sum(len(tokens)
                    for tokens in \
                    tokenized_lines) / len(tokenized_lines)

    # Build the base prompt.
    base_prompt = "Pick as many lines as you can from these poem lines:\n"
    base_msg = [{"role": "user", "content": base_prompt}]
    base_fmt = tokenizer.apply_chat_template(base_msg,
                                                add_generation_prompt=True,
                                                tokenize=False)
    base_offset = len(tokenizer(base_fmt).input_ids)
    if input_len <= base_offset:
        raise ValueError(
            f"'input_len' must be higher than the base prompt length "
            f"({base_offset}).")

    # Determine how many poem lines to use.
    num_input_lines = round((input_len - base_offset) / avg_len)
    num_prefix_lines = round((prefix_len - base_offset) / avg_len)
    num_prefix_lines = max(0, num_prefix_lines)
    prefix_lines = data[:num_prefix_lines]

    samples = []
    for _ in range(num_requests):
        extra_lines = random.choices(data,
                                        k=num_input_lines - num_prefix_lines)
        prompt = f"{base_prompt}{''.join(prefix_lines + extra_lines)}"
        msg = [{"role": "user", "content": prompt}]
        prompt_formatted = tokenizer.apply_chat_template(
            msg, add_generation_prompt=True, tokenize=False)
        prompt_len = len(tokenizer(prompt_formatted).input_ids)
        samples.append(
            SampleRequest(
                prompt=prompt_formatted
                if return_prompt_formatted else prompt,
                prompt_len=prompt_len,
                expected_output_len=output_len,
            ))
    return samples


def prompt_to_message(prompt, tokenizer, max_length, if_padding=False):
    if not if_padding:
        messages = [{"role": "user", "content": prompt}]
    else:
        messages = [{"role": "user", "content": prompt}]   
        prompt_formatted = tokenizer.apply_chat_template(
            messages, add_generation_prompt=True, tokenize=False)
        prompt_len = len(tokenizer(prompt_formatted).input_ids)
        while prompt_len < max_length:
            random_char  = random.choice(prompt)
            prompt = prompt + random_char
            messages = [{"role": "user", "content": prompt}]
            prompt_formatted = tokenizer.apply_chat_template(
                messages, add_generation_prompt=True, tokenize=False)
            prompt_len = len(tokenizer(prompt_formatted).input_ids)

        while prompt_len > max_length:
            prompt = prompt[:-1]
            messages = [{"role": "user", "content": prompt}]
            prompt_formatted = tokenizer.apply_chat_template(
                messages, add_generation_prompt=True, tokenize=False)
            prompt_len = len(tokenizer(prompt_formatted).input_ids)

    return messages

def performance_test(args, print_result=True, save_file=True):
    THREAD_NUM = args.thread_num
    INPUT_TOKENS_NUM = args.input_tokens_num
    OUTPUT_TOKENS_NUM = args.output_tokens_num
    MODEL_NAME = args.model_name
    PORT = args.port
    IP_ADDRESS = args.ip
    MODEL_PATH = args.model_path
    UNIFORM_INTERVAL = args.uniform_interval
    DATASET_PATH = args.dataset_path

    report_result = {
        "Process Num": THREAD_NUM,
        "Input Length": INPUT_TOKENS_NUM,
        "Output Length": OUTPUT_TOKENS_NUM,
        "TTFT (ms)": np.nan,
        "avg TPS (without prefill)": np.nan,
        "avg TPS (with prefill)": np.nan,
        "Total Time (ms)": np.nan,
        "TPS (without prefill)": np.nan,
        "TPS (with prefill)": np.nan,
        "Error": "",
        "avg input Tokens": 0,  # 初始化 Prompt Tokens
        "avg output Tokens": 0   # 初始化 Actual Tokens
    }
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    request_list = sample_sonnet_input(dataset_path=DATASET_PATH, 
                                       tokenizer=tokenizer, 
                                       num_requests=THREAD_NUM, 
                                       prefix_len=0, 
                                       input_len=INPUT_TOKENS_NUM, 
                                       output_len=OUTPUT_TOKENS_NUM, 
                                       return_prompt_formatted=False)
    parameters_list = []

    # 构造请求，每个请求的prompt均不相同
    for i in range(THREAD_NUM):
        messages = prompt_to_message(prompt=request_list[i].prompt, tokenizer=tokenizer, max_length=INPUT_TOKENS_NUM, if_padding=True)
        parameters = {
            "model": MODEL_NAME,
            "messages": messages,
            "stream": True,  # 启用流式
            "max_tokens": OUTPUT_TOKENS_NUM,
            "temperature": 0.6,
            "top_p": 0.95,
            "stream_options": {"include_usage": True},
            "skip_special_tokens": False,
            "ignore_eos": True
        }
        prompt_formatted = tokenizer.apply_chat_template(
            messages, add_generation_prompt=True, tokenize=False)
        input_tokens_num = len(tokenizer(prompt_formatted).input_ids)

        parameters_list.append({
            "parameters": parameters,
            "input_tokens_num": input_tokens_num,
        })

    # openai 接口
    URL = f"http://{IP_ADDRESS}:{PORT}/v1/chat/completions"  # OpenAI标准端点

    thread = ThreadPoolExecutor(max_workers=THREAD_NUM)
    total_dict = {}
    error = ""

    def test(i, start_time):
        headers = {"Content-type": "application/json"}
        parameters = parameters_list[i]["parameters"]
        input_tokens_num = parameters_list[i]["input_tokens_num"]
        result_ans = ""
        is_first_token = True

        # 根据均匀模式调整请求的启动时间
        if UNIFORM_INTERVAL > 0:
            delay = i * (UNIFORM_INTERVAL / THREAD_NUM)
            time.sleep(delay)
            true_start_time = time.time()
        else:
            true_start_time = start_time
        
        try:
            # 发送请求
            response = requests.post(url=URL, json=parameters, headers=headers, stream=True)
            for chunk in response.iter_lines():
                if chunk:
                    # 计算首 Token 时延
                    if is_first_token:
                        first_token_time = time.time() - true_start_time
                        
                        # 开始计时非首 Token 时延
                        non_first_token_time = time.time()
                        is_first_token = False

                    decoded = chunk.decode('utf-8')
                    if decoded.startswith('data:'):
                        data = decoded[5:].strip()
                        if data == '[DONE]':
                            break
                        temp_response = json.loads(data)
                        # print(temp_response)
                        if temp_response['choices']:
                            # 提取内容
                            delta = temp_response['choices'][0]['delta']
                            if 'content' in delta and delta['content'] is not None:
                                result_ans += delta['content']
                            elif 'reasoning_content' in delta and delta['reasoning_content'] is not None:
                                result_ans += delta['reasoning_content']
                            else:
                                print("未知的delta类型")    
        except Exception as e:
            print(f"第{i}个线程发生错误: {e}")
            return
        # 计算非首 Token 时延
        per_end_time = time.time()
        non_first_token_time = per_end_time - non_first_token_time
        infer_time = per_end_time - true_start_time

        total_dict[str(i)] = {
            "input_tokens_num": input_tokens_num,
    		"infer_time": infer_time,
            "first_token_time": first_token_time,
            "non_first_token_time": non_first_token_time,
            "contents": result_ans,
    	}
        return

    future_list = []
    start_time = time.time()
    for index in range(THREAD_NUM):
        future = thread.submit(test, index, start_time)
        future_list.append(future)

    for future in future_list:
        result = future.result()

    end_time = time.time()

    for k, v in total_dict.items():
        output_tokens_num = len(tokenizer.tokenize(v["contents"]))
        if output_tokens_num <= 1:
            total_dict[k].update({
            "output_tokens_num": output_tokens_num,
            "non_first_token_throughput": 0,
            "with_first_token_throughput": 0,
            "tpot": 0
        })
        else:
            total_dict[k].update({
                "output_tokens_num": output_tokens_num,
                "non_first_token_throughput": round((output_tokens_num - 1) / v['non_first_token_time'], 4),
                "with_first_token_throughput": round(output_tokens_num / v['infer_time'], 4),
                "tpot": round(v['non_first_token_time'] / (output_tokens_num - 1) * 1000, 4)
            })

    output_tokens_num_list = [v["output_tokens_num"] for k, v in total_dict.items()]
    input_tokens_num_list = [v["input_tokens_num"] for k, v in total_dict.items()]

    first_token_time_list = [v["first_token_time"] for k,v in total_dict.items()]
    non_first_token_throughput_list = [v["non_first_token_throughput"] for k,v in total_dict.items()]
    with_first_token_throughput_list = [v["with_first_token_throughput"] for k,v in total_dict.items()]
    tpot = [v["tpot"] for k,v in total_dict.items() if v["tpot"] > 0]
    success_requests = len(tpot)
    if success_requests == 0:
        error = "本次测试，所有的请求都返回了错误，请检查模型是否正常启动。"
        print(error)
        report_result.update({"Error": error})
        return report_result

    total_time = end_time - start_time

    if UNIFORM_INTERVAL > 0:
        TPS_with_prefill = round(sum(with_first_token_throughput_list), 4)
    else:
        TPS_with_prefill = round(sum(output_tokens_num_list) / total_time, 4)
    TPS_without_prefill = round(sum(non_first_token_throughput_list), 4)

    error_num = THREAD_NUM - success_requests
    if error_num > 0:
        error = f"本次测试失败的请求数: {error_num}"
        print(error)

    report_result.update({
        "TTFT (ms)": round((sum(first_token_time_list) / success_requests) * 1000, 4),
        "avg TPS (without prefill)": round(sum(non_first_token_throughput_list) / success_requests, 4),
        "avg TPS (with prefill)": round(sum(output_tokens_num_list) / total_time / success_requests, 4),
        "Total Time (ms)": total_time * 1000,
        "TPS (without prefill)": TPS_without_prefill,
        "TPS (with prefill)": TPS_with_prefill,
        "avg input Tokens": int(sum(input_tokens_num_list) / success_requests),  # 更新 Prompt Tokens
        "avg output Tokens": int(sum(output_tokens_num_list) / success_requests) ,
        "Error": error  # 更新 Actual Tokens
    })

    if print_result:
        print("=====================================================")
        print("Thread Num: {} | Input Tokens: {} | Output Tokens: {}".format(THREAD_NUM, INPUT_TOKENS_NUM, OUTPUT_TOKENS_NUM))
        print("=====================================================")
        print("Actual Success Request Num                  : {}".format(success_requests))
        print("Actual Input Token Num                      : {}".format(round(sum(input_tokens_num_list) / success_requests, 4)))                          # 输入Token总数 / 请求数
        print("Actual Output Token Num                     : {}".format(round(sum(output_tokens_num_list) / success_requests, 4)))                          # 输出Token总数 / 请求数
        print('=====================================================')
        print("Total TPS with    prefill(tokens/s)         : {}".format(TPS_with_prefill))                    # 总 输出Token 数 / 总推理时间
        print("Total TPS without prefill                   : {}".format(TPS_without_prefill))                 # 非首token 总 输出Token 数 / 总推理时间
        print("Mean TPS with    prefill                    : {}".format(round(TPS_with_prefill / success_requests, 4)))      # 平均首Token吞吐总和 / 请求数
        print("Mean TPS without prefill                    : {}".format(round(TPS_without_prefill / success_requests, 4)))      # 平均非首Token吞吐总和 / 请求数
        print('=====================================================')
        print("Mean TTFT(ms)                               : {}".format(round((sum(first_token_time_list) / success_requests) * 1000, 4)))       # 首Token时延总和 / 请求数
        print("Max  TTFT(ms)                               : {}".format(round(max(first_token_time_list) * 1000, 4)))                      # 最大首Token时延
        print("Min  TTFT(ms)                               : {}".format(round(min(first_token_time_list) * 1000, 4)))                      # 最小首Token时延
        print('=====================================================')
        print("Mean TPOT(ms)                               : {}".format(round((sum(tpot) / success_requests), 4)))   # 非首Token时延总和 / 请求数
        print("Max  TPOT(ms)                               : {}".format(round(max(tpot), 4)))                  # 最大非首Token时延
        print("Min  TPOT(ms)                               : {}".format(round(min(tpot), 4)))                  # 最小非首Token时延
        print('=====================================================')
        print("Total Time(s)                               : {}".format(round(total_time, 4)))                          # 总推理时间 [总推理时间=第一个请求发送 到 最后一个请求结束]
        print("Request Throughput(requests/s)              : {}".format(round(success_requests / total_time, 4)))                          # 请求数 / 总推理时间 [总推理时间=第一个请求发送 到 最后一个请求结束]
        print('=====================================================')


    if save_file:
        save_to_csv([report_result], args.csv_file)
        file_path = "./totoal_cost.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(total_dict, f, indent=4, ensure_ascii=False)
    
    return report_result


if __name__ == "__main__":
    # 添加argparse参数解析
    parser = argparse.ArgumentParser(description="Performance benchmark for a language model.")
    parser.add_argument("-P", '--thread-num', type=int, default=1, help='并发数')
    parser.add_argument("-I", '--input-tokens-num', type=int, default=2048, help='输入Token数')
    parser.add_argument("-O", '--output-tokens-num', type=int, default=2048, help='输出Token数')
    parser.add_argument("-M", '--model-name', type=str, default="qwen", help='模型服务化部署时的模型名称')
    parser.add_argument("-C", "--csv-file", type=str, default="results.csv", help="csv file to store results")
    parser.add_argument('--ip', type=str, default="127.0.0.1", help='Service IP Address')
    parser.add_argument('--port', type=int, default=1025, help='Service 端口')
    parser.add_argument('--model-path', type=str, default="", help='模型路径')
    parser.add_argument('--dataset-path', type=str, default="./sonnet_20x.txt", help='数据集路径')
    parser.add_argument('--warmup-num', type=int, default=0, help='预热请求数')
    parser.add_argument('--uniform-interval', type=float, default=0, help='均匀发起请求的时间间隔（秒），默认为0表示不启用均匀模式')
    args = parser.parse_args()

    if args.warmup_num > 0:
        print("Warmup requests: {}".format(args.warmup_num))
        args.thread_num = args.warmup_num
        performance_test(args=args, print_result=True, save_file=False)
    else:
        report_result = performance_test(args=args, print_result=True, save_file=True)
