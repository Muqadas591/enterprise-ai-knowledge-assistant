export async function withRetry(
  operation,
  {
    retries = 2,
    delay = 800,
  } = {}
) {
  let lastError;

  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      return await operation();
    } catch (error) {
      lastError = error;

      if (error?.name === "AbortError") {
        throw error;
      }

      if (attempt === retries) {
        break;
      }

      const backoff = delay * Math.pow(2, attempt);

      await new Promise((resolve) => setTimeout(resolve, backoff));
    }
  }

  throw lastError;
}
