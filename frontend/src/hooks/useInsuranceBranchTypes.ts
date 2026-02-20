import { useQuery } from '@tanstack/react-query'
import axiosInstance from '@/lib/axios'
import { API_ENDPOINTS } from '@/config/api'

export interface InsuranceBranchType {
  id: number
  nome: string
  codice: string
  descrizione?: string
  attivo: boolean
  created_at: string
  updated_at: string
}

export const useInsuranceBranchTypes = () => {
  return useQuery({
    queryKey: ['insurance-branch-types'],
    queryFn: async () => {
      const response = await axiosInstance.get<InsuranceBranchType[]>(
        API_ENDPOINTS.SYSTEM_INSURANCE_BRANCH_TYPES
      )
      return response.data || []
    },
    staleTime: 1000 * 60 * 5, // 5 minuti
    gcTime: 1000 * 60 * 10, // 10 minuti (ex: cacheTime)
  })
}
