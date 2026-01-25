/**
 * Login Form Component
 * 
 * Handles user login with form validation.
 * No auth logic - uses useAuth hook.
 */

import { useState, FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { LogIn, Loader2 } from 'lucide-react'
import { useAuth } from '@/hooks/useAuth'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { glassmorphism } from '@/lib/glassmorphism'
import { cn } from '@/lib/utils'

export function LoginForm() {
  const navigate = useNavigate()
  const { login, isLoading, error, clearError } = useAuth()

  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [localError, setLocalError] = useState<string | null>(null)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setLocalError(null)
    clearError()

    if (!username || !password) {
      setLocalError('Please enter both username and password')
      return
    }

    try {
      await login({ username, password })
      navigate('/dashboard', { replace: true })
    } catch (err: any) {
      // Error is handled by auth store
      setLocalError(err?.detail || 'Login failed')
    }
  }

  const displayError = localError || error

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className={cn(
        glassmorphism('dark', true, true),
        'rounded-2xl p-8 w-full max-w-md mx-auto'
      )}
    >
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold mb-2 bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
          Welcome Back
        </h1>
        <p className="text-muted-foreground">Sign in to your account</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {displayError && (
          <div className="p-4 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-sm">
            {displayError}
          </div>
        )}

        <div className="space-y-2">
          <label htmlFor="username" className="text-sm font-medium">
            Username or Email
          </label>
          <input
            id="username"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full px-4 py-3 rounded-lg bg-background/50 border border-white/20 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20 transition-all"
            placeholder="Enter username or email"
            disabled={isLoading}
            autoComplete="username"
          />
        </div>

        <div className="space-y-2">
          <label htmlFor="password" className="text-sm font-medium">
            Password
          </label>
          <Input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="bg-background/50 border-white/20"
            placeholder="Enter password"
            disabled={isLoading}
            autoComplete="current-password"
          />
        </div>

        <Button
          type="submit"
          className="w-full"
          disabled={isLoading}
        >
          {isLoading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Signing in...
            </>
          ) : (
            <>
              <LogIn className="mr-2 h-4 w-4" />
              Sign In
            </>
          )}
        </Button>
      </form>
    </motion.div>
  )
}
