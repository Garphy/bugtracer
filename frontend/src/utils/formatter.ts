import dayjs from 'dayjs'
import { marked } from 'marked'
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

// Configure marked
marked.setOptions({
  breaks: true,
  gfm: true,
})

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
  
  let text = content

  // 1. Convert [b]...[/b] to strong tag placeholder
  text = text.replace(/\[b\](.*?)\[\/b\]/gi, '<strong class="content-bold">$1</strong>')

  // 2. Parse Markdown
  let html = marked.parse(text) as string

  // 3. Inline Image / Attachment Mapping: 图1, 图2, ![图1], etc.
  const usedIndices = new Set<number>()

  // Handle standard markdown image with 图N e.g. ![图1](...) or ![1](...)
  html = html.replace(/<img[^>]*alt="图?(\d+)"[^>]*>/gi, (match, p1) => {
    const idx = parseInt(p1, 10) - 1
    if (idx >= 0 && idx < attachments.length) {
      usedIndices.add(idx)
      const att = attachments[idx]
      return `<span class="inline-block my-1.5"><a href="${att.url}" target="_blank" class="block border border-gray-300 rounded p-1 hover:border-blue-500 transition shadow-sm bg-white"><img src="${att.url}" alt="${att.original_name}" class="max-h-56 max-w-sm object-contain rounded" /><span class="block text-[11px] text-gray-500 mt-1 truncate max-w-[240px]">图${idx + 1}：${att.original_name}</span></a></span>`
    }
    return match
  })

  // Handle raw text references: 图1, 图2, ...
  html = html.replace(/图(\d+)/g, (match, p1) => {
    const idx = parseInt(p1, 10) - 1 // 1-based to 0-based
    if (idx >= 0 && idx < attachments.length) {
      usedIndices.add(idx)
      const att = attachments[idx]
      return `<span class="inline-block my-1.5 align-top"><span class="text-xs text-blue-600 font-semibold block mb-0.5">${match}：</span><a href="${att.url}" target="_blank" class="block border border-gray-300 rounded p-1 hover:border-blue-500 transition shadow-sm bg-white"><img src="${att.url}" alt="${att.original_name}" class="max-h-52 max-w-xs object-contain rounded" /><span class="block text-[10px] text-gray-500 mt-0.5 truncate max-w-[200px]">${att.original_name}</span></a></span>`
    }
    return match
  })

  // 4. Append unreferenced image attachments in a bottom gallery
  const otherImages = attachments.filter((att, index) => {
    const isImage = /\.(jpg|jpeg|png|gif|webp|svg|bmp)$/i.test(att.original_name)
    return isImage && !usedIndices.has(index)
  })

  if (otherImages.length > 0) {
    html += '<div class="mt-4 pt-3 border-t border-gray-200"><div class="text-xs font-semibold text-gray-500 mb-2">附件图片清单：</div><div class="flex flex-wrap gap-2.5">'
    otherImages.forEach((att, i) => {
      html += `<div class="text-center"><a href="${att.url}" target="_blank" class="block border border-gray-300 rounded p-1 hover:border-blue-500 transition shadow-sm bg-white"><img src="${att.url}" alt="${att.original_name}" class="h-24 w-24 object-cover rounded" /><span class="block text-[10px] text-gray-500 mt-1 truncate max-w-[100px]">${att.original_name}</span></a></div>`
    })
    html += '</div></div>'
  }

  return `<div class="markdown-body text-xs">${html}</div>`
}

export function formatDate(dateStr?: string): string {
  if (!dateStr) return ''
  return dayjs(dateStr).format('YYYY-MM-DD HH:mm')
}

export function formatShortDate(dateStr?: string): string {
  if (!dateStr) return ''
  return dayjs(dateStr).format('MM-DD HH:mm')
}
