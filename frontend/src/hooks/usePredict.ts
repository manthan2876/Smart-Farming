import { useMutation, useQueryClient } from '@tanstack/react-query'
import { predict } from '../api/predictions'
import { useAuth } from '../context/AuthContext'

export function usePredict() {
  const { token } = useAuth()
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ file, location, language }: { file: File; location: string; language: string }) => {
      if (!token) throw new Error('Sign in to run a live field check.')
      return predict(file, { location, language }, token)
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['history'] }),
  })
}
