export interface Business {
  id: string;
  name: string;
  address: string;
  city: string;
  state: string;
  zip_code: string;
  phone: string;
  email: string;
  cuisine_type: string;
  open_time: string;
  close_time: string;
}

export interface ManageRequest extends Business {
  business: Business;
}