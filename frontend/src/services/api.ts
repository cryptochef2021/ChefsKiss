import axios from "axios";
import type { Listing, SearchParams } from "../types/listing";

const api = axios.create({
  baseURL: "/api/v1",
});

export async function searchListings(
  params: SearchParams
): Promise<Listing[]> {
  const { data } = await api.get<Listing[]>("/listings/search", { params });
  return data;
}

export async function getListing(id: number): Promise<Listing> {
  const { data } = await api.get<Listing>(`/listings/${id}`);
  return data;
}

export async function compareListingPrices(id: number) {
  const { data } = await api.get(`/listings/${id}/compare`);
  return data;
}

export async function getHostReviews(hostId: number) {
  const { data } = await api.get(`/reviews/host/${hostId}`);
  return data;
}

export async function getAvailability(listingId: number) {
  const { data } = await api.get(`/calendar/listing/${listingId}/availability`);
  return data;
}
