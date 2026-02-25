import { z } from 'zod';

export const enrollmentSchema = z.object({
  group_id: z.string().min(1, "Please select a group"),
  family_id: z.string().min(1, "Please select a family record"),
  kid_name: z.string().min(2, "Student name must be at least 2 characters long"),
});
