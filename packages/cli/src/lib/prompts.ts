import {confirm} from '@inquirer/prompts'

export async function promptConfirm(message: string, defaultValue = false): Promise<boolean> {
  return confirm({default: defaultValue, message})
}
