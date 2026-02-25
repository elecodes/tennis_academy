import { z } from 'zod';

export const groupSchema = z.object({
  name: z.string().min(2, "Group name must be at least 2 characters long"),
  coach_id: z.string().min(1, "Please select a coach"),
  level: z.enum(["Beginner", "Intermediate", "Advanced"], {
    message: "Please select a valid level",
  }),
  capacity: z.preprocess((val) => Number(val), z.number().int().min(1, "Capacity must be at least 1")),
  schedule: z.string().min(2, "Please specify a schedule"),
});
