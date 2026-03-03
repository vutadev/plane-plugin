import chalk from 'chalk'
import Table from 'cli-table3'
import ora, {Ora} from 'ora'

export function formatTable(headers: string[], rows: string[][]): string {
  const table = new Table({
    head: headers.map((h) => chalk.cyan(h)),
    style: {border: [], head: []},
  })
  table.push(...rows)
  return table.toString()
}

export function printJson(data: unknown): void {
  console.log(JSON.stringify(data, null, 2))
}

export function createSpinner(text: string): Ora {
  return ora(text).start()
}

export function success(message: string): void {
  console.log(chalk.green('✓'), message)
}

export function error(message: string): void {
  console.error(chalk.red('✗'), message)
}

export function info(message: string): void {
  console.log(chalk.blue('ℹ'), message)
}

export function warning(message: string): void {
  console.log(chalk.yellow('⚠'), message)
}

// Priority colors
export function priorityColor(priority: string): string {
  const colors: Record<string, (s: string) => string> = {
    high: chalk.red,
    low: chalk.blue,
    medium: chalk.yellow,
    none: chalk.gray,
    urgent: chalk.red.bold,
  }
  return (colors[priority] || chalk.white)(priority.toUpperCase())
}

// State colors
export function stateColor(state: string, color?: string): string {
  if (color) {
    return chalk.hex(color)(state)
  }

  return chalk.white(state)
}

// Format date
export function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleDateString()
}

// Format datetime
export function formatDateTime(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleString()
}

// Strip HTML tags
export function stripHtml(html: string): string {
  return html
    .replaceAll(/<[^>]*>/g, ' ')
    .replaceAll(/\s+/g, ' ')
    .trim()
    .slice(0, 200)
}

// Truncate text
export function truncate(str: string, length: number): string {
  if (str.length <= length) return str
  return str.slice(0, length - 3) + '...'
}
