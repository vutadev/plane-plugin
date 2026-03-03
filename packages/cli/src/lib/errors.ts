import chalk from 'chalk'

export class PlaneCLIError extends Error {
  constructor(
    message: string,
    public code: string,
    public exitCode = 1,
  ) {
    super(message)
    this.name = 'PlaneCLIError'
  }
}

export class APIError extends Error {
  constructor(
    public status: number,
    message: string,
    public path: string,
  ) {
    super(`API Error ${status}: ${message}`)
    this.name = 'APIError'
  }
}

export function handleError(error: unknown): never {
  if (error instanceof PlaneCLIError) {
    console.error(chalk.red(`Error (${error.code}): ${error.message}`))
    process.exit(error.exitCode)
  }

  if (error instanceof APIError) {
    console.error(chalk.red(`API Error ${error.status}:`))
    console.error(chalk.gray(error.message))
    switch (error.status) {
    case 401: {
      console.error(chalk.yellow('Run `plane-cli config init` to set up authentication'))
    
    break;
    }

    case 403: {
      console.error(chalk.yellow('Permission denied. Check your API key or access token.'))
    
    break;
    }

    case 404: {
      console.error(chalk.yellow('Resource not found. Check the ID and try again.'))
    
    break;
    }

    default: { if (error.status >= 500) {
      console.error(chalk.yellow('Server error. Please try again later.'))
    }
    }
    }

    process.exit(1)
  }

  console.error(chalk.red('Unexpected error:'))
  console.error(error)
  process.exit(1)
}
