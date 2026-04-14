#!/usr/bin/env python3
import os
from pathlib import Path

def add_breadcrumb_to_file(filepath, breadcrumb_html):
    """Add breadcrumb navigation to an HTML file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find the header section
        header_start = content.find('<header')
        header_end = content.find('</header>', header_start) + 9

        if header_start != -1 and header_end != -1:
            # Insert breadcrumb after header
            new_content = content[:header_end] + '\n\n      ' + breadcrumb_html + '\n\n      ' + content[header_end:]

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)

            print(f"Added breadcrumb to {filepath}")
        else:
            print(f"Could not find header in {filepath}")
    except Exception as e:
        print(f"Error processing {filepath}: {e}")

def generate_breadcrumb(page_type, department=None, agent=None):
    """Generate breadcrumb HTML based on page type"""
    base_breadcrumb = '''
      <nav aria-label="Breadcrumb" class="flex items-center space-x-2 text-sm text-slate-600 dark:text-slate-400">
        <a href="index.html" class="hover:text-brand-600 dark:hover:text-brand-400 transition">Dashboard</a>
        <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M9 18l6-6-6-6" />
        </svg>'''

    if page_type == 'departments':
        breadcrumb = base_breadcrumb + '''
        <span class="text-slate-900 dark:text-slate-100 font-medium">Departments</span>
      </nav>'''
    elif page_type == 'agents':
        breadcrumb = base_breadcrumb + '''
        <a href="departments.html" class="hover:text-brand-600 dark:hover:text-brand-400 transition">Departments</a>
        <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M9 18l6-6-6-6" />
        </svg>
        <span class="text-slate-900 dark:text-slate-100 font-medium">All Agents</span>
      </nav>'''
    elif page_type == 'department':
        breadcrumb = base_breadcrumb + f'''
        <a href="departments.html" class="hover:text-brand-600 dark:hover:text-brand-400 transition">Departments</a>
        <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M9 18l6-6-6-6" />
        </svg>
        <span class="text-slate-900 dark:text-slate-100 font-medium">{department}</span>
      </nav>'''
    elif page_type == 'agent':
        breadcrumb = base_breadcrumb + f'''
        <a href="departments.html" class="hover:text-brand-600 dark:hover:text-brand-400 transition">Departments</a>
        <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M9 18l6-6-6-6" />
        </svg>
        <a href="{department.lower().replace(' ', '-')}.html" class="hover:text-brand-600 dark:hover:text-brand-400 transition">{department}</a>
        <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M9 18l6-6-6-6" />
        </svg>
        <span class="text-slate-900 dark:text-slate-100 font-medium">{agent}</span>
      </nav>'''
    else:
        breadcrumb = base_breadcrumb + '''
        <span class="text-slate-900 dark:text-slate-100 font-medium">Dashboard</span>
      </nav>'''

    return breadcrumb

def add_breadcrumbs_to_all_pages():
    """Add breadcrumb navigation to all HTML pages"""
    base_path = Path('/workspaces/agency-agents-njs')

    # Add breadcrumb to departments.html
    breadcrumb = generate_breadcrumb('departments')
    add_breadcrumb_to_file(base_path / 'departments.html', breadcrumb)

    # Add breadcrumb to agents.html
    breadcrumb = generate_breadcrumb('agents')
    add_breadcrumb_to_file(base_path / 'agents.html', breadcrumb)

    # Department mapping
    dept_files = {
        'academic.html': 'Academic',
        'design.html': 'Design',
        'engineering.html': 'Engineering',
        'finance.html': 'Finance',
        'game-development.html': 'Game Development',
        'marketing.html': 'Marketing',
        'paid-media.html': 'Paid Media',
        'product.html': 'Product',
        'project-management.html': 'Project Management',
        'sales.html': 'Sales',
        'spatial-computing.html': 'Spatial Computing',
        'specialized.html': 'Specialized',
        'support.html': 'Support',
        'testing.html': 'Testing'
    }

    # Add breadcrumbs to department pages
    for filename, dept_name in dept_files.items():
        filepath = base_path / filename
        if filepath.exists():
            breadcrumb = generate_breadcrumb('department', dept_name)
            add_breadcrumb_to_file(filepath, breadcrumb)

    # Add breadcrumbs to agent pages
    departments = [
        ('academic', 'Academic'),
        ('design', 'Design'),
        ('engineering', 'Engineering'),
        ('finance', 'Finance'),
        ('game-development', 'Game Development'),
        ('marketing', 'Marketing'),
        ('paid-media', 'Paid Media'),
        ('product', 'Product'),
        ('project-management', 'Project Management'),
        ('sales', 'Sales'),
        ('spatial-computing', 'Spatial Computing'),
        ('specialized', 'Specialized'),
        ('support', 'Support'),
        ('testing', 'Testing')
    ]

    for dept_folder, dept_display in departments:
        dept_path = base_path / dept_folder
        if dept_path.exists():
            for html_file in dept_path.glob('*.html'):
                # Extract agent name from filename
                agent_name = html_file.stem.replace('-', ' ').title()
                breadcrumb = generate_breadcrumb('agent', dept_display, agent_name)
                add_breadcrumb_to_file(html_file, breadcrumb)

        # Handle game-development subfolders
        if dept_folder == 'game-development':
            for subfolder in ['godot', 'roblox-studio', 'unity', 'unreal-engine']:
                sub_path = base_path / dept_folder / subfolder
                if sub_path.exists():
                    for html_file in sub_path.glob('*.html'):
                        agent_name = html_file.stem.replace('-', ' ').title()
                        breadcrumb = generate_breadcrumb('agent', dept_display, agent_name)
                        add_breadcrumb_to_file(html_file, breadcrumb)

if __name__ == '__main__':
    add_breadcrumbs_to_all_pages()