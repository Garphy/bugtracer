import dayjs from 'dayjs'
import { Attachment } from '../types'

export const STATUS_LIST = [
  { id: 0, code: 'closed', name: '已关闭', class: 'status-closed' },
  { id: 1, code: 'new', name: '新增', class: 'status-new' },
  { id: 2, code: 'key', name: '重要', class: 'status-key' },
  { id: 3, code: 'part_fixed', name: '部分处理', class: 'status-part_fixed' },
  { id: 4, code: 'fixed', name: '已解决', class: 'status-fixed' },
  { id: 5, code: 'wont_fix', name: '不处理', class: 'status-wont_fix' },
  { id: 6, code: 'todo', name: '待办', class: 'status-todo' },
  { id: 7, code: 'idea', name: '备忘', class: 'status-idea' },
]

export function escapeHtml(str: string): string {
  if (!str) return ''
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;')
}

export function formatBugContent(content: string, attachments: Attachment[] = []): string {
  if (!content) return ''
  
  let html = escapeHtml(content)

  // 1. [b]...[/b] -> <strong class="content-bold">...</strong>
  html = html.replace(/\[b\](.*?)\[\/b\]/gi, '<strong class="content-bold">$1</strong>')

  // 2. URLs -> Clickable Links
  html = html.replace(
    /(https?:\/\/[^\s<]+)/g,
    '<a href="$1" target="_blank" rel="noopener noreferrer" class="content-link">$1</a>'
  )

  // 3. Newlines -> <br/>
  html = html.replace(/\n/g, '<br/>')

  // 4. Inline Image Mapping: 图1, 图2, ...
  const usedIndices = new Set<number>()
  html = html.replace(/图(\d+)/g, (match, p1) => {
    const idx = parseInt(p1, 10) - 1 // 1-based to 0-based
    if (idx >= 0 && idx < attachments.length) {
      usedIndices.add(idx)
      const att = attachments[idx]
      return `<span class="inline-block my-1"><span class="text-xs text-blue-600 font-medium">${match}：</span><a href="${att.url}" target="_blank" class="inline-block align-middle border border-gray-300 rounded p-0.5 hover:border-blue-500 transition"><img src="${att.url}" alt="${att.original_name}" class="max-h-48 max-w-xs object-contain rounded" /></a></span>`
    }
    return match
  })

  // 5. Append unreferenced image attachments
  const otherImages = attachments.filter((att, index) => {
    const isImage = /\.(jpg|jpeg|png|gif|webp|svg|bmp)$/i.test(att.original_name)
    return isImage && !usedIndices.has(index)
  })

  if (otherImages.length > 0) {
    html += '<div class="mt-3 pt-2 border-t border-gray-100 flex flex-wrap gap-2">'
    otherImages.forEach((att, i) => {
      html += `<div class="text-center"><a href="${att.url}" target="_blank" class="block border border-gray-300 rounded p-1 hover:border-blue-500 transition"><img src="${att.url}" alt="${att.original_name}" class="h-28 w-28 object-cover rounded" /><span class="block text-xs text-gray-500 mt-1 truncate max-w-[110px]">${att.original_name}</span></a></div>`
    })
    html += '</div>'
  }

  return html
}

export function formatDate(dateStr?: string): string {
  if (!dateStr) return ''
  return dayjs(dateStr).format('YYYY-MM-DD HH:mm')
}

export function formatShortDate(dateStr?: string): string {
  if (!dateStr) return ''
  return dayjs(dateStr).format('MM-DD HH:mm')
}
