"use client"

import * as React from "react"
import clsx from 'clsx'

interface NavButton {
  className?: string
  children: React.ReactNode
  variant?: 'default' | 'outline'
  onClick?: () => void
}

const Button: React.FC<NavButton> = ({ 
  className, 
  children, 
  variant = 'default',
  onClick 
}) => {
  return (
    <button
      onClick={onClick}
      className={clsx(
        'inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2',
        'disabled:pointer-events-none disabled:opacity-50',
        'h-10 px-4 py-2',
        variant === 'default' && [
          'bg-black text-white hover:bg-black/90',
          'dark:bg-white dark:text-black dark:hover:bg-white/90'
        ],
        variant === 'outline' && [
          'border border-current',
          'hover:bg-black/10 dark:hover:bg-white/10'
        ],
        className
      )}
    >
      {children}
    </button>
  )
}

interface NavItem {
  to?: string
  text: string
  items?: {
    icon?: {
      dark: string
      light: string
    }
    text: string
    description?: string
    to: string
  }[]
}

interface HeaderProps {
  className?: string
  theme?: 'light' | 'dark'
  isSticky?: boolean
  isStickyOverlay?: boolean
  withBorder?: boolean
  logo?: React.ReactNode
  menuItems?: NavItem[]
  onThemeChange?: () => void
  rightContent?: React.ReactNode
}

const ChevronIcon = () => (
  <svg
    width="10"
    height="6"
    viewBox="0 0 10 6"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    className="w-2.5 opacity-60 [&_path]:stroke-2"
  >
    <path d="M1 1L5 5L9 1" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
)

const Navigation: React.FC<{ isDarkTheme?: boolean; items: NavItem[] }> = ({ isDarkTheme, items }) => (
  <nav>
    <ul className="flex gap-x-10 xl:gap-x-8 lg:hidden [@media(max-width:1070px)]:gap-x-6">
      {items.map(({ to, text, items }, index) => {
        const Tag = to ? 'a' : 'button'
        return (
          <li
            className={clsx('relative [perspective:2000px]', items?.length > 0 && 'group')}
            key={index}
          >
            <Tag
              className={clsx(
                'flex items-center gap-x-1 whitespace-pre text-sm',
                isDarkTheme ? 'text-white' : 'text-black dark:text-white'
              )}
              href={to}
            >
              {text}
              {items?.length > 0 && <ChevronIcon />}
            </Tag>
            {items?.length > 0 && (
              <div
                className={clsx(
                  'absolute -left-5 top-full w-[300px] pt-5',
                  'pointer-events-none opacity-0',
                  'origin-top-left transition-[opacity,transform] duration-200 [transform:rotateX(-12deg)_scale(0.9)]',
                  'group-hover:pointer-events-auto group-hover:visible group-hover:opacity-100 group-hover:[transform:none]'
                )}
              >
                <ul
                  className={clsx(
                    'relative flex min-w-[248px] flex-col gap-y-0.5 rounded-[14px] border p-2.5',
                    'dark:border-[#16181D] dark:bg-[#0B0C0F] dark:shadow-[0px_14px_20px_0px_rgba(0,0,0,.5)]',
                    isDarkTheme
                      ? 'border-[#16181D] bg-[#0B0C0F] shadow-[0px_14px_20px_0px_rgba(0,0,0,.5)]'
                      : 'border-gray-200 bg-white shadow-[0px_14px_20px_0px_rgba(0,0,0,.1)]'
                  )}
                >
                  {items.map(({ icon, text, description, to }, index) => (
                    <li key={index}>
                      <a
                        className={clsx(
                          'group/link relative flex items-center overflow-hidden whitespace-nowrap rounded-[14px] p-2',
                          'before:absolute before:inset-0 before:z-10 before:opacity-0 before:transition-opacity before:duration-200 hover:before:opacity-100',
                          isDarkTheme
                            ? 'text-white before:bg-[#16181D]'
                            : 'text-black before:bg-[#f5f5f5]'
                        )}
                        href={to}
                      >
                        {icon && (
                          <div
                            className={clsx(
                              'relative z-10 flex h-10 w-10 shrink-0 items-center justify-center rounded-lg border',
                              isDarkTheme
                                ? 'border-[#2E3038] bg-[#16181D]'
                                : 'border-gray-200 bg-[#F5F5F5]'
                            )}
                          >
                            <img
                              className="h-5 w-5"
                              src={isDarkTheme ? icon.dark : icon.light}
                              width={20}
                              height={20}
                              loading="lazy"
                              alt=""
                              aria-hidden
                            />
                          </div>
                        )}
                        <div className="relative z-10 ml-3">
                          <span className="block text-sm font-medium">{text}</span>
                          {description && (
                            <span
                              className={clsx(
                                'mt-0.5 block text-sm',
                                isDarkTheme ? 'text-gray-400' : 'text-gray-500'
                              )}
                            >
                              {description}
                            </span>
                          )}
                        </div>
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </li>
        )
      })}
    </ul>
  </nav>
)

const MobileMenuButton: React.FC<{ onClick: () => void; isDarkTheme?: boolean }> = ({
  onClick,
  isDarkTheme,
}) => (
  <button
    className={clsx(
      'hidden lg:block',
      'relative h-8 w-8',
      isDarkTheme ? 'text-white' : 'text-black dark:text-white'
    )}
    onClick={onClick}
  >
    <span className="absolute left-1/2 top-1/2 block h-0.5 w-5 -translate-x-1/2 -translate-y-1/2 rounded-full bg-current" />
    <span className="absolute left-1/2 top-1/2 block h-0.5 w-5 -translate-x-1/2 translate-y-1 rounded-full bg-current" />
  </button>
)

export const Header: React.FC<HeaderProps> = ({
  className,
  theme = 'light',
  isSticky = false,
  isStickyOverlay = false,
  withBorder = false,
  logo,
  menuItems = [],
  onThemeChange,
  rightContent,
}) => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = React.useState(false)
  const isDarkTheme = theme === 'dark'

  return (
    <header
      className={clsx(
        'relative z-40 w-full',
        isSticky && 'sticky top-0',
        isStickyOverlay && 'bg-white/80 backdrop-blur-md dark:bg-[#0B0C0F]/80',
        withBorder && 'border-b border-gray-200 dark:border-[#16181D]',
        className
      )}
    >
      <div className="mx-auto max-w-[1760px] px-5 py-4">
        <div className="flex items-center justify-between">
          {logo}
          <Navigation isDarkTheme={isDarkTheme} items={menuItems} />
          <div className="flex items-center gap-x-6">
            {rightContent}
            {onThemeChange && (
              <Button
                variant="default"
                onClick={onThemeChange}
              >
                {isDarkTheme ? '🌞' : '🌙'}
              </Button>
            )}
            <MobileMenuButton
              isDarkTheme={isDarkTheme}
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            />
          </div>
        </div>
      </div>
    </header>
  )
}

export { Button }
export default Header