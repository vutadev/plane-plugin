import chalk from 'chalk'

export class CLIError extends Error {
  constructor(
    message: string,
    public code: string,
    public exitCode = 1,
  ) {
    super(message)
    this.name = 'CLIError'
  }
}

export function handleError(error: unknown): never {
  if (error instanceof CLIError) {
    console.error(chalk.red(`Error (${error.code}): ${error.message}`))
    process.exit(error.exitCode)
  }

  console.error(chalk.red('Unexpected error:'))
  console.error(error)
  process.exit(1)
}
