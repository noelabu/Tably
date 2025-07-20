export interface User {
  id: string;
  email: string;
  full_name?: string;
  role: 'customer' | 'business-owner';
  created_at?: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token?: string;
  token_type: string;
  expires_in?: number;
}

export interface LoginResponse {
  access_token: string;
  refresh_token?: string;
  token_type: string;
  expires_in?: number;
}

export interface SignupResponse extends LoginResponse {
  user: User;
}

export interface RefreshTokenResponse extends LoginResponse {
  user: User;
}