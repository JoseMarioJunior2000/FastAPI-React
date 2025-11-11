import { handleApi } from "./handleApi";

export async function loginUser(email, password) {
  return handleApi("/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}