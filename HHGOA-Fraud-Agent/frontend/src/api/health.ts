import { apiClient } from './client';
import type { ApiResponse, HealthResponse, HealthDependenciesResponse } from '../types/api';

export async function getSystemHealth(): Promise<HealthResponse> {
  const res = await apiClient.get<ApiResponse<HealthResponse>>('/health');
  return res.data.data;
}

export async function getDependencyHealth(): Promise<HealthDependenciesResponse> {
  const res = await apiClient.get<ApiResponse<HealthDependenciesResponse>>('/health/dependencies');
  return res.data.data;
}
