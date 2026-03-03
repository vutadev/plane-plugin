export async function getLatestVersion(packageName: string): Promise<null | string> {
  try {
    const res = await fetch(`https://registry.npmjs.org/${packageName}/latest`, {
      headers: {
        Accept: 'application/json',
      },
    })

    if (!res.ok) {
      return null
    }

    const data = await res.json() as {version: string}
    return data.version
  } catch {
    return null
  }
}
