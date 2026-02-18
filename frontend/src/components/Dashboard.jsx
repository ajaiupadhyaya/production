import React, { useState, useEffect } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
} from '@mui/material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import ShowChartIcon from '@mui/icons-material/ShowChart';
import axios from 'axios';

export default function Dashboard() {
  const [portfolio, setPortfolio] = useState(null);
  const [strategies, setStrategies] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [portfolioRes, strategiesRes] = await Promise.all([
        axios.get('/api/portfolio'),
        axios.get('/api/strategies'),
      ]);
      setPortfolio(portfolioRes.data);
      setStrategies(strategiesRes.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const portfolioData = [
    { date: '1/1', value: 100000 },
    { date: '1/2', value: 101500 },
    { date: '1/3', value: 103200 },
    { date: '1/4', value: 102800 },
    { date: '1/5', value: 105600 },
    { date: '1/6', value: 107200 },
  ];

  const StatCard = ({ title, value, icon, color }) => (
    <Card sx={{ height: '100%', bgcolor: '#131b3a' }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box>
            <Typography color="text.secondary" gutterBottom>
              {title}
            </Typography>
            <Typography variant="h4" component="div" sx={{ color }}>
              {value}
            </Typography>
          </Box>
          <Box sx={{ color, fontSize: 48 }}>
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  if (loading) {
    return <Typography>Loading...</Typography>;
  }

  const totalValue = portfolio?.total_value || 100000;
  const pnl = portfolio?.pnl?.total_pnl || 0;
  const returnPct = portfolio?.pnl?.return_pct || 0;

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
        Dashboard Overview
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <StatCard
            title="Portfolio Value"
            value={`$${totalValue.toLocaleString()}`}
            icon={<AccountBalanceIcon />}
            color="#00d4ff"
          />
        </Grid>
        <Grid item xs={12} md={4}>
          <StatCard
            title="Total P&L"
            value={`$${pnl.toLocaleString()}`}
            icon={<TrendingUpIcon />}
            color={pnl >= 0 ? '#4caf50' : '#f44336'}
          />
        </Grid>
        <Grid item xs={12} md={4}>
          <StatCard
            title="Return"
            value={`${returnPct.toFixed(2)}%`}
            icon={<ShowChartIcon />}
            color={returnPct >= 0 ? '#4caf50' : '#f44336'}
          />
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 3, bgcolor: '#131b3a' }}>
            <Typography variant="h6" gutterBottom>
              Portfolio Performance
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={portfolioData}>
                <defs>
                  <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#00d4ff" stopOpacity={0.8} />
                    <stop offset="95%" stopColor="#00d4ff" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#2a3f5f" />
                <XAxis dataKey="date" stroke="#8884d8" />
                <YAxis stroke="#8884d8" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#131b3a', border: '1px solid #00d4ff' }}
                />
                <Area
                  type="monotone"
                  dataKey="value"
                  stroke="#00d4ff"
                  fillOpacity={1}
                  fill="url(#colorValue)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 3, bgcolor: '#131b3a' }}>
            <Typography variant="h6" gutterBottom>
              Active Strategies
            </Typography>
            {strategies.length > 0 ? (
              <Grid container spacing={2}>
                {strategies.slice(0, 4).map((strategy) => (
                  <Grid item xs={12} md={6} key={strategy.id}>
                    <Card sx={{ bgcolor: '#0a0e27' }}>
                      <CardContent>
                        <Typography variant="h6">{strategy.name}</Typography>
                        <Typography color="text.secondary">
                          {strategy.strategy_type}
                        </Typography>
                        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between' }}>
                          <Box>
                            <Typography variant="caption" color="text.secondary">
                              P&L
                            </Typography>
                            <Typography
                              variant="body1"
                              sx={{
                                color: strategy.total_pnl >= 0 ? '#4caf50' : '#f44336',
                              }}
                            >
                              ${strategy.total_pnl?.toFixed(2) || '0.00'}
                            </Typography>
                          </Box>
                          <Box>
                            <Typography variant="caption" color="text.secondary">
                              Win Rate
                            </Typography>
                            <Typography variant="body1">
                              {(strategy.win_rate * 100 || 0).toFixed(1)}%
                            </Typography>
                          </Box>
                          <Box>
                            <Typography variant="caption" color="text.secondary">
                              Sharpe
                            </Typography>
                            <Typography variant="body1">
                              {strategy.sharpe_ratio?.toFixed(2) || '0.00'}
                            </Typography>
                          </Box>
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            ) : (
              <Typography color="text.secondary">
                No active strategies. Create one to get started.
              </Typography>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
