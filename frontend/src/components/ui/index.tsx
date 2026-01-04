import { forwardRef, InputHTMLAttributes, ReactNode } from 'react'
import { motion, HTMLMotionProps } from 'framer-motion'
import { Loader2, LucideIcon } from 'lucide-react'

// ========================================
// Glass Card Component
// ========================================

interface GlassCardProps extends HTMLMotionProps<'div'> {
  children: ReactNode
  variant?: 'default' | 'health' | 'happiness' | 'hela'
  hover?: boolean
  glow?: boolean
}

export const GlassCard = forwardRef<HTMLDivElement, GlassCardProps>(
  ({ children, variant = 'default', hover = false, glow = false, className = '', ...props }, ref) => {
    const variantClasses = {
      default: '',
      health: 'section-card-health',
      happiness: 'section-card-happiness',
      hela: 'section-card-hela',
    }

    const glowClasses = {
      default: '',
      health: 'glow-health',
      happiness: 'glow-happiness',
      hela: 'glow-hela',
    }

    return (
      <motion.div
        ref={ref}
        className={`
          glass-card p-6
          ${variantClasses[variant]}
          ${hover ? 'glass-card-hover' : ''}
          ${glow ? glowClasses[variant] : ''}
          ${className}
        `}
        {...props}
      >
        {children}
      </motion.div>
    )
  }
)

GlassCard.displayName = 'GlassCard'

// ========================================
// Glow Button Component
// ========================================

interface GlowButtonProps {
  children?: ReactNode
  variant?: 'primary' | 'secondary' | 'success' | 'danger' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
  icon?: LucideIcon
  iconPosition?: 'left' | 'right'
  fullWidth?: boolean
  className?: string
  disabled?: boolean
  type?: 'button' | 'submit' | 'reset'
  onClick?: () => void
}

export const GlowButton = forwardRef<HTMLButtonElement, GlowButtonProps>(
  ({
    children,
    variant = 'primary',
    size = 'md',
    loading = false,
    icon: Icon,
    iconPosition = 'left',
    fullWidth = false,
    className = '',
    disabled,
    type = 'button',
    onClick,
  }, ref) => {
    const variantClasses = {
      primary: 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white shadow-lg shadow-purple-500/25',
      secondary: 'bg-white/10 hover:bg-white/20 text-white border border-white/20',
      success: 'bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white shadow-lg shadow-emerald-500/25',
      danger: 'bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 text-white shadow-lg shadow-red-500/25',
      ghost: 'bg-transparent hover:bg-white/10 text-white/70 hover:text-white',
    }

    const sizeClasses = {
      sm: 'px-3 py-1.5 text-sm gap-1.5',
      md: 'px-4 py-2.5 text-sm gap-2',
      lg: 'px-6 py-3 text-base gap-2.5',
    }

    const iconSizes = {
      sm: 'w-3.5 h-3.5',
      md: 'w-4 h-4',
      lg: 'w-5 h-5',
    }

    return (
      <motion.button
        ref={ref}
        type={type}
        whileHover={{ scale: disabled ? 1 : 1.02 }}
        whileTap={{ scale: disabled ? 1 : 0.98 }}
        className={`
          btn-glow inline-flex items-center justify-center font-medium rounded-xl
          transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed
          ${variantClasses[variant]}
          ${sizeClasses[size]}
          ${fullWidth ? 'w-full' : ''}
          ${className}
        `}
        disabled={disabled || loading}
        onClick={onClick}
      >
        {loading ? (
          <Loader2 className={`${iconSizes[size]} animate-spin`} />
        ) : (
          <>
            {Icon && iconPosition === 'left' && <Icon className={iconSizes[size]} />}
            {children}
            {Icon && iconPosition === 'right' && <Icon className={iconSizes[size]} />}
          </>
        )}
      </motion.button>
    )
  }
)

GlowButton.displayName = 'GlowButton'

// ========================================
// Input Field Component
// ========================================

interface InputFieldProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  icon?: LucideIcon
  fullWidth?: boolean
}

export const InputField = forwardRef<HTMLInputElement, InputFieldProps>(
  ({ label, error, icon: Icon, fullWidth = true, className = '', ...props }, ref) => {
    return (
      <div className={`${fullWidth ? 'w-full' : ''}`}>
        {label && (
          <label className="block text-sm font-medium text-white/80 mb-2">
            {label}
          </label>
        )}
        <div className="relative">
          {Icon && (
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-white/40">
              <Icon className="w-5 h-5" />
            </div>
          )}
          <input
            ref={ref}
            className={`
              input-glow w-full px-4 py-3 text-white
              ${Icon ? 'pl-11' : ''}
              ${error ? 'border-red-500 focus:border-red-500 focus:ring-red-500/20' : ''}
              ${className}
            `}
            {...props}
          />
        </div>
        {error && (
          <motion.p
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-2 text-sm text-red-400"
          >
            {error}
          </motion.p>
        )}
      </div>
    )
  }
)

InputField.displayName = 'InputField'

// ========================================
// Textarea Component
// ========================================

interface TextareaFieldProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string
  error?: string
  fullWidth?: boolean
}

export const TextareaField = forwardRef<HTMLTextAreaElement, TextareaFieldProps>(
  ({ label, error, fullWidth = true, className = '', ...props }, ref) => {
    return (
      <div className={`${fullWidth ? 'w-full' : ''}`}>
        {label && (
          <label className="block text-sm font-medium text-white/80 mb-2">
            {label}
          </label>
        )}
        <textarea
          ref={ref}
          className={`
            input-glow w-full px-4 py-3 text-white resize-none
            ${error ? 'border-red-500 focus:border-red-500 focus:ring-red-500/20' : ''}
            ${className}
          `}
          {...props}
        />
        {error && (
          <motion.p
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-2 text-sm text-red-400"
          >
            {error}
          </motion.p>
        )}
      </div>
    )
  }
)

TextareaField.displayName = 'TextareaField'

// ========================================
// Select Component
// ========================================

interface SelectOption {
  value: string | number
  label: string
}

interface SelectFieldProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string
  options: SelectOption[]
  icon?: LucideIcon
  fullWidth?: boolean
}

export const SelectField = forwardRef<HTMLSelectElement, SelectFieldProps>(
  ({ label, options, icon: Icon, fullWidth = true, className = '', ...props }, ref) => {
    return (
      <div className={`${fullWidth ? 'w-full' : ''}`}>
        {label && (
          <label className="block text-sm font-medium text-white/80 mb-2">
            {label}
          </label>
        )}
        <div className="relative">
          {Icon && (
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-white/40 pointer-events-none">
              <Icon className="w-5 h-5" />
            </div>
          )}
          <select
            ref={ref}
            className={`
              input-glow w-full px-4 py-3 text-white appearance-none cursor-pointer
              bg-[url('data:image/svg+xml;charset=utf-8,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%2224%22%20height%3D%2224%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22rgba(255%2C255%2C255%2C0.5)%22%20stroke-width%3D%222%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpath%20d%3D%22m6%209%206%206%206-6%22%2F%3E%3C%2Fsvg%3E')]
              bg-[length:1.5rem] bg-[right_0.5rem_center] bg-no-repeat pr-10
              ${Icon ? 'pl-11' : ''}
              ${className}
            `}
            {...props}
          >
            {options.map((option) => (
              <option key={option.value} value={option.value} className="bg-gray-900 text-white">
                {option.label}
              </option>
            ))}
          </select>
        </div>
      </div>
    )
  }
)

SelectField.displayName = 'SelectField'

// ========================================
// Loading Spinner Component
// ========================================

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg'
  text?: string
}

export function LoadingSpinner({ size = 'md', text }: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: 'w-6 h-6 border-2',
    md: 'w-10 h-10 border-3',
    lg: 'w-16 h-16 border-4',
  }

  return (
    <div className="flex flex-col items-center justify-center gap-4">
      <div className={`spinner ${sizeClasses[size]}`} />
      {text && <p className="text-white/60 text-sm">{text}</p>}
    </div>
  )
}

// ========================================
// Badge Component
// ========================================

interface BadgeProps {
  children: ReactNode
  variant?: 'default' | 'owner' | 'success' | 'warning' | 'error'
  icon?: LucideIcon
}

export function Badge({ children, variant = 'default', icon: Icon }: BadgeProps) {
  const variantClasses = {
    default: 'bg-white/10 text-white/70',
    owner: 'bg-gradient-to-r from-purple-600 to-pink-600 text-white',
    success: 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30',
    warning: 'bg-amber-500/20 text-amber-400 border border-amber-500/30',
    error: 'bg-red-500/20 text-red-400 border border-red-500/30',
  }

  return (
    <span className={`badge ${variantClasses[variant]}`}>
      {Icon && <Icon className="w-3 h-3" />}
      {children}
    </span>
  )
}

// ========================================
// Icon Button Component
// ========================================

interface IconButtonProps {
  icon: LucideIcon
  variant?: 'default' | 'danger' | 'success'
  size?: 'sm' | 'md' | 'lg'
  tooltip?: string
  className?: string
  disabled?: boolean
  type?: 'button' | 'submit' | 'reset'
  onClick?: () => void
}

export const IconButton = forwardRef<HTMLButtonElement, IconButtonProps>(
  ({ icon: Icon, variant = 'default', size = 'md', tooltip, className = '', disabled, type = 'button', onClick }, ref) => {
    const sizeClasses = {
      sm: 'w-8 h-8',
      md: 'w-10 h-10',
      lg: 'w-12 h-12',
    }

    const iconSizes = {
      sm: 'w-4 h-4',
      md: 'w-5 h-5',
      lg: 'w-6 h-6',
    }

    const variantClasses = {
      default: '',
      danger: 'icon-btn-danger',
      success: 'hover:bg-emerald-500/20 hover:border-emerald-500/40 hover:text-emerald-400',
    }

    return (
      <motion.button
        ref={ref}
        type={type}
        disabled={disabled}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        className={`icon-btn ${sizeClasses[size]} ${variantClasses[variant]} ${tooltip ? 'tooltip' : ''} ${className}`}
        data-tooltip={tooltip}
        onClick={onClick}
      >
        <Icon className={iconSizes[size]} />
      </motion.button>
    )
  }
)

IconButton.displayName = 'IconButton'

// ========================================
// Progress Bar Component
// ========================================

interface ProgressBarProps {
  value: number
  max?: number
  showLabel?: boolean
  size?: 'sm' | 'md' | 'lg'
}

export function ProgressBar({ value, max = 100, showLabel = false, size = 'md' }: ProgressBarProps) {
  const percentage = Math.min((value / max) * 100, 100)

  const sizeClasses = {
    sm: 'h-1.5',
    md: 'h-2.5',
    lg: 'h-4',
  }

  return (
    <div className="w-full">
      {showLabel && (
        <div className="flex justify-between text-sm text-white/60 mb-1">
          <span>Progress</span>
          <span>{Math.round(percentage)}%</span>
        </div>
      )}
      <div className={`progress-bar-container ${sizeClasses[size]}`}>
        <motion.div
          className="progress-bar-fill"
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
        />
      </div>
    </div>
  )
}

// ========================================
// Page Container Component
// ========================================

interface PageContainerProps {
  children: ReactNode
  className?: string
}

export function PageContainer({ children, className = '' }: PageContainerProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className={`max-w-6xl mx-auto px-4 py-6 ${className}`}
    >
      {children}
    </motion.div>
  )
}

// ========================================
// Page Title Component
// ========================================

interface PageTitleProps {
  title: string
  subtitle?: string
  icon?: LucideIcon
  action?: ReactNode
}

export function PageTitle({ title, subtitle, icon: Icon, action }: PageTitleProps) {
  return (
    <div className="flex items-center justify-between mb-8">
      <div className="flex items-center gap-4">
        {Icon && (
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500/20 to-pink-500/20 border border-white/10 flex items-center justify-center">
            <Icon className="w-6 h-6 text-purple-400" />
          </div>
        )}
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white">{title}</h1>
          {subtitle && <p className="text-white/50 mt-1">{subtitle}</p>}
        </div>
      </div>
      {action && <div>{action}</div>}
    </div>
  )
}

// ========================================
// Empty State Component
// ========================================

interface EmptyStateProps {
  icon?: LucideIcon
  title: string
  description?: string
  action?: ReactNode
}

export function EmptyState({ icon: Icon, title, description, action }: EmptyStateProps) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="glass-card p-12 text-center"
    >
      {Icon && (
        <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-white/5 flex items-center justify-center">
          <Icon className="w-8 h-8 text-white/40" />
        </div>
      )}
      <h3 className="text-lg font-semibold text-white mb-2">{title}</h3>
      {description && <p className="text-white/50 mb-6">{description}</p>}
      {action}
    </motion.div>
  )
}
