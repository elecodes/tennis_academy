import { z } from 'zod';

export const groupSchema = z.object({
  name: z.string().min(2, "Group name must be at least 2 characters long"),
  coach_id: z.string().optional().or(z.literal('')),
  schedule: z.string().min(2, "Please specify a schedule"),
});
