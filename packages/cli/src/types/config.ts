import {z} from 'zod'

export const ConfigSchema = z.object({
  accessToken: z.string().optional(),
  apiKey: z.string().optional(),
  baseUrl: z.string().default('https://api.plane.so/api/v1'),
  currentProfile: z.string().default('default'),
  defaults: z
    .object({
      project: z.string().optional(),
    })
    .optional(),
  profiles: z
    .record(
      z.string(),
      z.object({
        accessToken: z.string().optional(),
        apiKey: z.string().optional(),
        workspace: z.string(),
      }),
    )
    .optional(),
  workspace: z.string(),
})

export type PlaneConfig = z.infer<typeof ConfigSchema>
