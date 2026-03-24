#!/usr/bin/env node
/**
 * good-skills CLI
 * Usage:
 *   npx good-skills run <skill>
 *   npx good-skills list
 *   npx good-skills archive
 */

import { execSync } from 'child_process'
import { fileURLToPath } from 'url'
import { dirname, resolve } from 'path'

const __dirname = dirname(fileURLToPath(import.meta.url))
const REPO = resolve(__dirname, '..')
const RUN = `${REPO}/scripts/run_skill.sh`

const SKILLS = {
  fitness:    ['skills/super-fitness/run_fitness.py'],
  wardrobe:   ['skills/super-wardrobe/run_wardrobe.py'],
  newsletter: ['skills/daily-newsletter/run_daily_newsletter.py', '--now'],
  arxiv:      ['skills/arxiv-daily/run_arxiv_daily.py'],
  vibe:       ['skills/vibe-daily/run_vibe_daily.py'],
  weekly:     ['skills/weekly-report/run_weekly_report.py'],
  digest:     ['skills/daily-digest/run_daily_digest.py'],
}

const [,, cmd, ...rest] = process.argv

if (cmd === 'list') {
  console.log('Available skills:')
  Object.keys(SKILLS).forEach(k => console.log(`  ${k}`))
  process.exit(0)
}

if (cmd === 'archive') {
  execSync(`bash ${REPO}/scripts/archive.sh`, { stdio: 'inherit', cwd: REPO })
  process.exit(0)
}

if (cmd === 'run') {
  const skill = rest[0]
  if (!skill || !SKILLS[skill]) {
    console.error(`Unknown skill: ${skill}`)
    console.error(`Available: ${Object.keys(SKILLS).join(', ')}`)
    process.exit(1)
  }
  const [script, ...args] = SKILLS[skill]
  execSync(`bash ${RUN} ${script} ${args.join(' ')}`, { stdio: 'inherit', cwd: REPO })
  process.exit(0)
}

console.log(`good-skills v1.0.0
Usage:
  npx good-skills list              # 列出所有 skill
  npx good-skills run <skill>       # 运行指定 skill
  npx good-skills archive           # 归档生成文件

Skills: ${Object.keys(SKILLS).join(', ')}`)
