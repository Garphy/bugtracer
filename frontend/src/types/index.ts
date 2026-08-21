export interface User {
  id: number
  username: string
  fullname: string
  role: 'admin' | 'coder' | 'tester' | 'guest'
  is_active: boolean
  api_key?: string
  created_at?: string
}

export interface UserSimple {
  id: number
  username: string
  fullname: string
  role: string
}

export interface Project {
  id: number
  name: string
  description: string
  default_version: string
  is_active: boolean
  created_at?: string
  active_bugs_count: number
  my_bugs_count: number
}

export interface Module {
  id: number
  project_id: number
  name: string
  sort_order: number
  bug_count?: number
}

export interface ProjectDetail extends Project {
  modules: Module[]
  members: UserSimple[]
}

export interface Attachment {
  id: number
  bug_id?: number
  project_id: number
  original_name: string
  stored_name: string
  file_size: number
  mime_type: string
  url: string
  created_at?: string
}

export interface Comment {
  id: number
  bug_id: number
  user_id?: number
  user?: UserSimple
  content: string
  created_at: string
}

export interface Activity {
  id: number
  bug_id: number
  user_id?: number
  user?: UserSimple
  action_type: string
  old_value: string
  new_value: string
  detail: string
  created_at: string
}

export interface BugListItem {
  id: number
  project_id: number
  project_name: string
  module_id?: number
  module_name: string
  status: number
  status_code: string
  status_name: string
  ver: string
  content: string
  has_attachment: boolean
  creator_id?: number
  creator_name: string
  assignee_id?: number
  assignee_name: string
  last_changer_name?: string
  is_assigned_to_me: boolean
  priority: number
  created_at: string
  updated_at: string
}

export interface BugDetail extends BugListItem {
  creator?: UserSimple
  assignee?: UserSimple
  last_changer?: UserSimple
  close_reason?: string
  fixed_at?: string
  attachments: Attachment[]
  comments: Comment[]
  activities: Activity[]
}

export interface BugListResponse {
  total: number
  page: number
  page_size: number
  total_pages: number
  items: BugListItem[]
  counts_summary: {
    shown: number
    total_in_project: number
  }
}

export interface MemberStat {
  user_id: number
  fullname: string
  username: string
  role: string
  active_count: number
  fixed_count: number
  key_count: number
  total_count: number
}

export interface ModuleStat {
  module_id: number
  module_name: string
  active_count: number
  fixed_count: number
  total_count: number
}

export interface ProjectStatsReport {
  project_id: number
  project_name: string
  total_bugs: number
  active_bugs: number
  fixed_bugs: number
  closed_bugs: number
  key_bugs: number
  member_stats: MemberStat[]
  module_stats: ModuleStat[]
  status_distribution: Record<string, number>
  daily_trend: Array<{ date: string; created: number; fixed: number }>
}

export interface FullProjectReportResponse {
  project_id: number
  project_name: string
  stats: ProjectStatsReport
  bugs_by_module: Record<string, BugListItem[]>
}
