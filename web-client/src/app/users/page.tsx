'use client'

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import './users.css';

interface User {
  username: string;
  email: string;
  role: string;
  groups: string[];
  rate_limit_duration: number;
  rate_limit_duration_type: string;
  throttle_duration: number;
  throttle_duration_type: string;
  throttle_wait_duration: number;
  throttle_wait_duration_type: string;
  throttle_queue_limit: number | null;
  custom_attributes: Record<string, string>;
  active: boolean;
}

const menuItems = [
  { label: 'Dashboard', href: '/dashboard' },
  { label: 'APIs', href: '/apis' },
  { label: 'Routings', href: '/routings' },
  { label: 'Users', href: '/users' },
  { label: 'Groups', href: '/groups' },
  { label: 'Roles', href: '/roles' },
  { label: 'Monitor', href: '/monitor' },
  { label: 'Logs', href: '/logging' },
  { label: 'Security', href: '/security' },
  { label: 'Settings', href: '/settings' },
];

const handleLogout = () => {
  localStorage.clear();
  sessionStorage.clear();
  setTimeout(() => {
    window.location.replace('/');
  }, 50);
};

const UsersPage = () => {
  const router = useRouter();
  const [users, setUsers] = useState<User[]>([]);
  const [allUsers, setAllUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('username');

  useEffect(() => {}, []);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`http://localhost:3002/platform/user/all?page=1&page_size=10`, {
        credentials: 'include',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'Cookie': `access_token_cookie=${document.cookie.split('; ').find(row => row.startsWith('access_token_cookie='))?.split('=')[1]}`
        }
      });
      if (!response.ok) {
        throw new Error('Failed to load users');
      }
      const data = await response.json();
      setAllUsers(data.users);
      setUsers(data.users);
    } catch (err) {
      setError('Failed to load users. Please try again later.');
      setUsers([]);
      setAllUsers([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchTerm.trim()) {
      setUsers(allUsers);
      return;
    }
    
    const filteredUsers = allUsers.filter(user => 
      user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.role.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.groups.some(group => group.toLowerCase().includes(searchTerm.toLowerCase()))
    );
    setUsers(filteredUsers);
  };

  const handleSort = (sortField: string) => {
    setSortBy(sortField);
    const sortedUsers = [...users].sort((a, b) => {
      if (sortField === 'username') {
        return a.username.localeCompare(b.username);
      } else if (sortField === 'role') {
        return a.role.localeCompare(b.role);
      } else if (sortField === 'status') {
        return a.active ? 1 : -1;
      }
      return 0;
    });
    setUsers(sortedUsers);
  };

  const handleUserClick = (user: User) => {
    // Store user data in sessionStorage for the detail page
    sessionStorage.setItem('selectedUser', JSON.stringify(user));
    router.push(`/users/${user.username}`);
  };

  const formatDuration = (duration: number | null | undefined, durationType: string | null | undefined) => {
    if (!duration || !durationType) return 'Not set';
    
    const plural = duration !== 1 && (durationType.endsWith('minute') || durationType.endsWith('second') || durationType.endsWith('hour')) ? 's' : '';
    return `${duration} ${durationType}${plural}`;
  };

  return (
    <>
      <div className="users-topbar">
      Doorman
      </div>
      <div className="users-root">
        <aside className="users-sidebar">
          <div className="users-sidebar-title">Menu</div>
          <ul className="users-sidebar-list">
            {menuItems.map((item, idx) => (
              item.href ? (
                <li key={item.label} className={`users-sidebar-item${idx === 3 ? ' active' : ''}`}>
                  <Link href={item.href} style={{ color: 'inherit', textDecoration: 'none', display: 'block', width: '100%' }}>{item.label}</Link>
                </li>
              ) : (
                <li key={item.label} className={`users-sidebar-item${idx === 3 ? ' active' : ''}`}>{item.label}</li>
              )
            ))}
          </ul>
          <button className="users-logout-btn" onClick={handleLogout}>
            Logout
          </button>
        </aside>
        <main className="users-main">
          <div className="users-header-row">
            <h1 className="users-title">Users</h1>
            <button className="refresh-button" onClick={fetchUsers}>
              <span className="refresh-icon">↻</span>
              Refresh
            </button>
          </div>

          <div className="users-controls">
            <form className="users-search-box" onSubmit={handleSearch}>
              <input
                type="text"
                className="users-search-input"
                placeholder="Search users..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
              <button type="submit" className="users-search-btn">Search</button>
              <Link href="/users/add" className="users-add-btn" style={{ textDecoration: 'none', display: 'inline-block' }}>
                Add User
              </Link>
            </form>
            <div className="users-sort-group">
              <button 
                className={`users-sort-btn ${sortBy === 'username' ? 'active' : ''}`}
                onClick={() => handleSort('username')}
              >
                Name
              </button>
              <button 
                className={`users-sort-btn ${sortBy === 'role' ? 'active' : ''}`}
                onClick={() => handleSort('role')}
              >
                Role
              </button>
              <button 
                className={`users-sort-btn ${sortBy === 'status' ? 'active' : ''}`}
                onClick={() => handleSort('status')}
              >
                Status
              </button>
            </div>
          </div>

          {error && (
            <div className="error-container">
              <div className="error-message">
                {error}
              </div>
            </div>
          )}

          {loading ? (
            <div className="loading-spinner">
              <div className="spinner"></div>
              <p>Loading users...</p>
            </div>
          ) : (
            <div className="users-table-panel">
              <table className="users-table">
                <thead>
                  <tr>
                    <th>Username</th>
                    <th>Email</th>
                    <th>Role</th>
                    <th>Groups</th>
                    <th>Rate Limit</th>
                    <th>Throttle</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((user) => (
                    <tr 
                      key={user.username} 
                      onClick={() => handleUserClick(user)}
                      style={{ cursor: 'pointer' }}
                      onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f5f5f5'}
                      onMouseLeave={(e) => e.currentTarget.style.backgroundColor = ''}
                    >
                      <td>{user.username}</td>
                      <td>{user.email}</td>
                      <td>{user.role}</td>
                      <td>{user.groups.length > 0 ? user.groups[0] : ''}</td>
                      <td>{formatDuration(user.rate_limit_duration, user.rate_limit_duration_type)}</td>
                      <td>{formatDuration(user.throttle_duration, user.throttle_duration_type)}</td>
                      <td>
                        <span className={`status-badge ${user.active ? 'active' : 'inactive'}`}>
                          {user.active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </main>
      </div>
    </>
  );
};

export default UsersPage;