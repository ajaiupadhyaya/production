import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  TextField,
  Button,
} from '@mui/material';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import SearchIcon from '@mui/icons-material/Search';

export default function Analytics() {
  const [symbol, setSymbol] = useState('SPY');

  const performanceData = [
    { month: 'Jan', return: 5.2, benchmark: 3.1 },
    { month: 'Feb', return: 7.8, benchmark: 4.5 },
    { month: 'Mar', return: -2.1, benchmark: -1.2 },
    { month: 'Apr', return: 9.4, benchmark: 5.7 },
    { month: 'May', return: 6.3, benchmark: 4.2 },
    { month: 'Jun', return: 11.2, benchmark: 7.8 },
  ];

  const riskMetrics = [
    { metric: 'Sharpe Ratio', value: 2.34 },
    { metric: 'Sortino Ratio', value: 3.12 },
    { metric: 'Max Drawdown', value: -8.5 },
    { metric: 'Volatility', value: 12.3 },
  ];

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
        Analytics & Insights
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper sx={{ p: 3, bgcolor: '#131b3a' }}>
            <Typography variant="h6" gutterBottom>
              Market Analysis
            </Typography>
            <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
              <TextField
                label="Symbol"
                value={symbol}
                onChange={(e) => setSymbol(e.target.value)}
                size="small"
              />
              <Button variant="contained" startIcon={<SearchIcon />}>
                Analyze
              </Button>
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, bgcolor: '#131b3a' }}>
            <Typography variant="h6" gutterBottom>
              Strategy Performance vs Benchmark
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={performanceData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2a3f5f" />
                <XAxis dataKey="month" stroke="#8884d8" />
                <YAxis stroke="#8884d8" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#131b3a', border: '1px solid #00d4ff' }}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="return"
                  stroke="#00d4ff"
                  name="Strategy Return (%)"
                />
                <Line
                  type="monotone"
                  dataKey="benchmark"
                  stroke="#ff6b00"
                  name="Benchmark (%)"
                />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, bgcolor: '#131b3a', height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              Risk Metrics
            </Typography>
            <Box sx={{ mt: 3 }}>
              {riskMetrics.map((metric) => (
                <Box
                  key={metric.metric}
                  sx={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    mb: 2,
                    pb: 2,
                    borderBottom: '1px solid #2a3f5f',
                  }}
                >
                  <Typography>{metric.metric}</Typography>
                  <Typography
                    sx={{
                      color: metric.value >= 0 ? '#4caf50' : '#f44336',
                      fontWeight: 'bold',
                    }}
                  >
                    {metric.value}
                    {metric.metric.includes('Ratio') ? '' : '%'}
                  </Typography>
                </Box>
              ))}
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 3, bgcolor: '#131b3a' }}>
            <Typography variant="h6" gutterBottom>
              Monthly Returns Distribution
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={performanceData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2a3f5f" />
                <XAxis dataKey="month" stroke="#8884d8" />
                <YAxis stroke="#8884d8" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#131b3a', border: '1px solid #00d4ff' }}
                />
                <Legend />
                <Bar dataKey="return" fill="#00d4ff" name="Monthly Return (%)" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 3, bgcolor: '#131b3a' }}>
            <Typography variant="h6" gutterBottom>
              AI-Powered Market Insights
            </Typography>
            <Card sx={{ bgcolor: '#0a0e27', mt: 2 }}>
              <CardContent>
                <Typography variant="subtitle1" gutterBottom sx={{ color: '#00d4ff' }}>
                  📊 Market Sentiment Analysis
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  Current market conditions show moderate bullish sentiment with increasing
                  momentum in technology sector. Risk-adjusted positioning recommended.
                </Typography>
                <Typography variant="subtitle1" gutterBottom sx={{ color: '#00d4ff', mt: 2 }}>
                  🎯 Strategy Recommendations
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  1. Momentum strategies showing strong performance
                  <br />
                  2. Consider reducing exposure in overvalued sectors
                  <br />
                  3. Volatility expected to decrease in next 2 weeks
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Last updated: {new Date().toLocaleString()}
                </Typography>
              </CardContent>
            </Card>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
