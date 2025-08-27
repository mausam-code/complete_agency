import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  Box,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
  Divider,
  Avatar,
  Chip,
} from '@mui/material';
import {
  Dashboard,
  People,
  Work,
  Assignment,
  Schedule,
  EventNote,
  Receipt,
  Payment,
  Business,
} from '@mui/icons-material';
import { useAuth } from '../../contexts/AuthContext';

const Sidebar = ({ onItemClick }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, canManageUsers, canViewFinancialData } = useAuth();

  const menuItems = [
    {
      text: 'Dashboard',
      icon: <Dashboard />,
      path: '/dashboard',
      show: true,
    },
    {
      text: 'Users',
      icon: <People />,
      path: '/users',
      show: canManageUsers(),
    },
    {
      text: 'Projects',
      icon: <Work />,
      path: '/projects',
      show: user?.level <= 2,
    },
    {
      text: 'Tasks',
      icon: <Assignment />,
      path: '/tasks',
      show: true,
    },
    {
      text: 'Attendance',
      icon: <Schedule />,
      path: '/attendance',
      show: true,
    },
    {
      text: 'Leave Requests',
      icon: <EventNote />,
      path: '/leave-requests',
      show: true,
    },
    {
      text: 'Expenses',
      icon: <Receipt />,
      path: '/expenses',
      show: true,
    },
    {
      text: 'Payroll',
      icon: <Payment />,
      path: '/payroll',
      show: canViewFinancialData() || user?.level === 3,
    },
  ];

  const handleItemClick = (path) => {
    navigate(path);
    if (onItemClick) onItemClick();
  };

  const getUserBadgeColor = (level) => {
    switch (level) {
      case 1: return 'error';
      case 2: return 'warning';
      case 3: return 'success';
      default: return 'default';
    }
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ p: 2, textAlign: 'center', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
        <Business sx={{ fontSize: 40, mb: 1 }} />
        <Typography variant="h6" sx={{ fontWeight: 'bold', fontSize: '1rem', lineHeight: 1.2 }}>
          {process.env.REACT_APP_COMPANY_NAME}
        </Typography>
        <Typography variant="caption" sx={{ opacity: 0.8 }}>
          Management System
        </Typography>
      </Box>

      {/* User Info */}
      <Box sx={{ p: 2, textAlign: 'center', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
        <Avatar
          sx={{
            width: 60,
            height: 60,
            mx: 'auto',
            mb: 1,
            bgcolor: `${getUserBadgeColor(user?.level)}.main`,
            border: '2px solid rgba(255,255,255,0.3)',
          }}
        >
          {user?.first_name?.[0] || user?.username?.[0] || 'U'}
        </Avatar>
        <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
          {user?.first_name} {user?.last_name}
        </Typography>
        <Chip
          label={user?.role_display || user?.role}
          color={getUserBadgeColor(user?.level)}
          size="small"
          sx={{ mt: 0.5 }}
        />
      </Box>

      {/* Navigation */}
      <Box sx={{ flex: 1, overflow: 'auto' }}>
        <List sx={{ p: 1 }}>
          {menuItems
            .filter(item => item.show)
            .map((item) => (
              <ListItem key={item.text} disablePadding sx={{ mb: 0.5 }}>
                <ListItemButton
                  onClick={() => handleItemClick(item.path)}
                  selected={location.pathname.startsWith(item.path)}
                  sx={{
                    borderRadius: 2,
                    '&.Mui-selected': {
                      bgcolor: 'rgba(255,255,255,0.15)',
                      '&:hover': {
                        bgcolor: 'rgba(255,255,255,0.2)',
                      },
                    },
                    '&:hover': {
                      bgcolor: 'rgba(255,255,255,0.1)',
                    },
                  }}
                >
                  <ListItemIcon sx={{ color: 'inherit', minWidth: 40 }}>
                    {item.icon}
                  </ListItemIcon>
                  <ListItemText 
                    primary={item.text}
                    primaryTypographyProps={{
                      fontSize: '0.875rem',
                      fontWeight: location.pathname.startsWith(item.path) ? 'bold' : 'normal',
                    }}
                  />
                </ListItemButton>
              </ListItem>
            ))}
        </List>
      </Box>

      {/* Footer */}
      <Box sx={{ p: 2, borderTop: '1px solid rgba(255,255,255,0.1)' }}>
        <Typography variant="caption" sx={{ opacity: 0.6, textAlign: 'center', display: 'block' }}>
          © 2025 J.K. OVERSEAS PVT.LTD.
        </Typography>
      </Box>
    </Box>
  );
};

export default Sidebar;
