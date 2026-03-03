import {checkbox, confirm, input, password, select} from '@inquirer/prompts'

export async function promptText(message: string, defaultValue?: string): Promise<string> {
  return input({default: defaultValue, message})
}

export async function promptPassword(message: string): Promise<string> {
  return password({mask: '*', message})
}

export async function promptSelect<T extends string>(
  message: string,
  choices: Array<{name: string; value: T;}>,
): Promise<T> {
  return select({choices, message})
}

export async function promptMultiSelect<T extends string>(
  message: string,
  choices: Array<{name: string; value: T;}>,
): Promise<T[]> {
  return checkbox({choices, message})
}

export async function promptConfirm(message: string, defaultValue = false): Promise<boolean> {
  return confirm({default: defaultValue, message})
}

export async function promptApiKey(): Promise<string> {
  return promptPassword('Enter your Plane API key (starts with "plane_api_")')
}

export async function promptAccessToken(): Promise<string> {
  return promptPassword('Enter your Plane access token')
}

export async function promptWorkspace(): Promise<string> {
  return promptText('Enter your workspace slug')
}

export async function promptBaseUrl(): Promise<string> {
  return promptText('Plane API base URL', 'https://api.plane.so/api/v1')
}
