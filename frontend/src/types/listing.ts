export interface Listing {
  id: number;
  title: string;
  title_translated: string | null;
  description_translated: string | null;
  city: string;
  country: string;
  price_per_night: number | null;
  price_per_month: number | null;
  currency: string;
  property_type: string | null;
  bedrooms: number | null;
  bathrooms: number | null;
  max_guests: number | null;
  platform_name: string | null;
  host_name: string | null;
  listing_url: string;
  latitude: number | null;
  longitude: number | null;
  rating: number | null;
  review_count: number;
  aggregate_host_rating: number | null;
  total_host_reviews: number;
}

export interface SearchParams {
  city?: string;
  country?: string;
  min_price?: number;
  max_price?: number;
  price_type?: "nightly" | "monthly";
  property_type?: string;
  min_bedrooms?: number;
  platforms?: string;
  sort_by?: "price" | "rating" | "reviews";
  page?: number;
  page_size?: number;
}
