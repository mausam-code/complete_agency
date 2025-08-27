import React from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  People,
  Work,
  Assignment,
  Receipt,
  TrendingUp,
  Schedule,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { userService } from '../services/users';

const StatCard = ({ title, value, icon, color = 'primary', subtitle }) => (
  <Card sx={{ height: '100%' }}>
    <CardContent>
      <Box display="flex" alignItems="center" justifyContent="space-between">
        <Box>
          <Typography color="textSecondary" gutterBottom variant="h6">
            {title}
          </Typography>
          <Typography variant="h4" component="h2" color={`${color}.main`}>
            {value}
          </Typography>
          {subtitle && (
            <Typography variant="body2" color="textSecondary">
              {subtitle}
            </Typography>
          )}
        </Box>
        <Box
          sx={{
            bgcolor: `${color}.main`,
            color: 'white',
            borderRadius: '50%',
            width: 60,
            height: 60,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          {icon}
        </Box>
      </Box>
    </CardContent>
  </Card>
);

const DashboardPage = () => {
  const { user } = useAuth();

  const { data: stats, isLoading, error } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: userService.getDashboardStats,
  });

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error">
        Failed to load dashboard data: {error.message}
      </Alert>
    );
  }

  const renderStatCards = () => {
    if (user?.role === 'superadmin') {
      return (
        <>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Total Users"
              value={stats?.total_users || 0}
              icon={<People />}
              color="primary"
              subtitle="All system users"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Total Projects"
              value={stats?.total_projects || 0}
              icon={<Work />}
              color="success"
              subtitle="All projects"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Active Projects"
              value={stats?.active_projects || 0}
              icon={<TrendingUp />}
              color="info"
              subtitle="In progress"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Pending Expenses"
              value={stats?.pending_expenses || 0}
              icon={<Receipt />}
              color="warning"
              subtitle="Awaiting approval"
            />
          </Grid>
        </>
      );
    } else if (user?.level === 2) {
      return (
        <>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Team Members"
              value={stats?.team_members || 0}
              icon={<People />}
              color="primary"
              subtitle="Under management"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="My Projects"
              value={stats?.my_projects || 0}
              icon={<Work />}
              color="success"
              subtitle="Projects managed"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Pending Tasks"
              value={stats?.pending_tasks || 0}
              icon={<Assignment />}
              color="warning"
              subtitle="Team tasks pending"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Pending Leaves"
              value={stats?.pending_leaves || 0}
              icon={<Schedule />}
              color="info"
              subtitle="Awaiting approval"
            />
          </Grid>
        </>
      );
    } else {
      return (
        <>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="My Tasks"
              value={stats?.my_tasks || 0}
              icon={<Assignment />}
              color="primary"
              subtitle="Total assigned"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Pending Tasks"
              value={stats?.pending_tasks || 0}
              icon={<Schedule />}
              color="warning"
              subtitle="Need attention"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="My Projects"
              value={stats?.my_projects || 0}
              icon={<Work />}
              color="success"
              subtitle="Active projects"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Leave Requests"
              value={stats?.my_leaves || 0}
              icon={<Receipt />}
              color="info"
              subtitle="This year"
            />
          </Grid>
        </>
      );
    }
  };

  const getDashboardTitle = () => {
    if (user?.role === 'superadmin') return 'Super Admin Dashboard';
    if (user?.level === 2) return 'Management Dashboard';
    return 'Employee Dashboard';
  };

  const getDashboardSubtitle = () => {
    if (user?.role === 'superadmin') return 'Complete system overview and control';
    if (user?.level === 2) return 'Team management and oversight';
    return 'Your personal workspace and tasks';
  };

  return (
    <Box>
      {/* Header */}
      <Box mb={4}>
        <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
          {getDashboardTitle()}
        </Typography>
        <Typography variant="subtitle1" color="textSecondary">
          Welcome back, {user?.first_name}! {getDashboardSubtitle()}
        </Typography>
      </Box>

      {/* Statistics Cards */}
      <Grid container spacing={3} mb={4}>
        {renderStatCards()}
      </Grid>

      {/* Additional Content */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Activity
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Activity feed will be implemented here showing recent actions,
                notifications, and system updates.
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quick Actions
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Quick action buttons will be implemented here for common tasks
                like creating projects, marking attendance, or submitting requests.
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DashboardPage;
