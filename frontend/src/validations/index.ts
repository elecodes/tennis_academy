import { userSchema } from './userSchema';
import { groupSchema } from './groupSchema';
import { enrollmentSchema } from './enrollmentSchema';
import { loginSchema } from './loginSchema';

export const validateUser = (data: any) => userSchema.safeParse(data);
export const validateGroup = (data: any) => groupSchema.safeParse(data);
export const validateEnrollment = (data: any) => enrollmentSchema.safeParse(data);
export const validateLogin = (data: any) => loginSchema.safeParse(data);

// Expose to window for use in templates
(window as any).Validations = {
  validateUser,
  validateGroup,
  validateEnrollment,
  validateLogin,
};
