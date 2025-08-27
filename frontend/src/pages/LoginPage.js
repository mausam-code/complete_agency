import React, { useState } from 'react';
import { Navigate } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  CircularProgress,
  Container,
  Avatar,
  Chip,
  Grid,
} from '@mui/material';
import { Business as BusinessIcon } from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

const LoginPage = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login, isAuthenticated } = useAuth();

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await login(username, password);
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  const demoAccounts = [
    { username: 'superadmin', password: 'admin123', role: 'Super Admin', level: 1, color: 'error' },
    { username: 'admin', password: 'admin123', role: 'Admin', level: 2, color: 'warning' },
    { username: 'hr_manager', password: 'admin123', role: 'HR Manager', level: 2, color: 'warning' },
    { username: 'accountant', password: 'admin123', role: 'Accountant', level: 2, color: 'warning' },
    { username: 'employee1', password: 'emp123', role: 'Employee', level: 3, color: 'success' },
    { username: 'customer1', password: 'cust123', role: 'Customer', level: 3, color: 'success' },
  ];

  const handleDemoLogin = (demoUsername, demoPassword) => {
    setUsername(demoUsername);
    setPassword(demoPassword);
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        p: 2,
      }}
    >
      <Container maxWidth="md">
        <Grid container spacing={4} alignItems="center">
          <Grid item xs={12} md={6}>
            <Card sx={{ maxWidth: 400, mx: 'auto' }}>
              <CardContent sx={{ p: 4 }}>
                <Box textAlign="center" mb={3}>
                  <Avatar
                    sx={{
                      width: 80,
                      height: 80,
                      bgcolor: 'primary.main',
                      mx: 'auto',
                      mb: 2,
                    }}
                  >
                    <BusinessIcon sx={{ fontSize: 40 }} />
                  </Avatar>
                  <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
                    {process.env.REACT_APP_COMPANY_NAME}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Management System
                  </Typography>
                </Box>

                <Box component="form" onSubmit={handleSubmit}>
                  <TextField
                    fullWidth
                    label="Username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    margin="normal"
                    required
                    autoFocus
                  />
                  <TextField
                    fullWidth
                    label="Password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    margin="normal"
                    required
                  />

                  {error && (
                    <Alert severity="error" sx={{ mt: 2 }}>
                      {error}
                    </Alert>
                  )}

                  <Button
                    type="submit"
                    fullWidth
                    variant="contained"
                    size="large"
                    disabled={loading}
                    sx={{ mt: 3, mb: 2, py: 1.5 }}
                  >
                    {loading ? <CircularProgress size={24} /> : 'Sign In'}
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card sx={{ bgcolor: 'rgba(255,255,255,0.1)', backdropFilter: 'blur(10px)' }}>
              <CardContent sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom color="white" textAlign="center">
                  Demo Accounts
                </Typography>
                <Typography variant="body2" color="rgba(255,255,255,0.8)" textAlign="center" mb={2}>
                  Click any account to auto-fill login credentials
                </Typography>

                <Grid container spacing={1}>
                  {demoAccounts.map((account) => (
                    <Grid item xs={12} sm={6} key={account.username}>
                      <Card
                        sx={{
                          cursor: 'pointer',
                          transition: 'transform 0.2s',
                          '&:hover': { transform: 'translateY(-2px)' },
                        }}
                        onClick={() => handleDemoLogin(account.username, account.password)}
                      >
                        <CardContent sx={{ p: 2 }}>
                          <Box display="flex" justifyContent="space-between" alignItems="center">
                            <Box>
                              <Typography variant="subtitle2" fontWeight="bold">
                                {account.username}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                {account.password}
                              </Typography>
                            </Box>
                            <Chip
                              label={account.role}
                              color={account.color}
                              size="small"
                            />
                          </Box>
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>

                <Typography variant="caption" color="rgba(255,255,255,0.6)" textAlign="center" display="block" mt={2}>
                  Choose any demo account to explore the system features
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};

export default LoginPage;
