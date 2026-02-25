import { z } from 'zod';

export const userSchema = z.object({
  full_name: z.string().min(2, "Name must be at least 2 characters long"),
  email: z.string().email("Invalid email address"),
  role: z.enum(["admin", "coach", "family"], {
    message: "Please select a valid role",
  }),
  phone: z.string().optional().or(z.literal('')),
  password: z.string().min(6, "Password must be at least 6 characters long").optional().or(z.literal('')),
});

export type UserFormData = z.infer<typeof userSchema>;
