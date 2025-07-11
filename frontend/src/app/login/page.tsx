import AuthInterface from '@/components/auth-interface'
import AuthGuard from '@/components/auth-guard'

export default function LoginPage() {
  return (
    <AuthGuard requireAuth={false}>
      <AuthInterface />
    </AuthGuard>
  )
}