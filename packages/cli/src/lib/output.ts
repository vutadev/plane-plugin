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
