import * as Sentry from "@sentry/browser";
import { userSchema } from './userSchema';

Sentry.init({
  dsn: (window as any).SENTRY_DSN || "",
  integrations: [
    Sentry.browserTracingIntegration(),
    Sentry.replayIntegration(),
  ],
  // Performance Monitoring
  tracesSampleRate: 1.0, //  Capture 100% of the transactions
  // Session Replay
  replaysSessionSampleRate: 0.1, // This sets the sample rate at 10%. You may want to change it to 100% while in development and then sample at a lower rate in production.
  replaysOnErrorSampleRate: 1.0, // If you're not already sampling the entire session, change the sample rate to 100% when sampling sessions where errors occur.
});

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
