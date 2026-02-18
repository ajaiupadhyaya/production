import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Grid,
  Card,
  CardContent,
} from '@mui/material';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
} from 'recharts';
import axios from 'axios';

const COLORS = ['#00d4ff', '#ff6b00', '#4caf50', '#f44336', '#9c27b0', '#ff9800'];

export default function Portfolio() {
  const [portfolio, setPortfolio] = useState(null);
  const [positions, setPositions] = useState([]);

  useEffect(() => {
    fetchPortfolioData();
  }, []);

  const fetchPortfolioData = async () => {
    try {
      const [portfolioRes, positionsRes] = await Promise.all([
        axios.get('/api/portfolio'),
        axios.get('/api/portfolio/positions'),
      ]);
      setPortfolio(portfolioRes.data);
      setPositions(positionsRes.data);
    } catch (error) {
      console.error('Error fetching portfolio data:', error);
    }
  };

  const pieData = positions.map((pos) => ({
    name: pos.symbol,
    value: pos.quantity * (pos.current_price || pos.entry_price),
  }));

  const totalValue = portfolio?.total_value || 0;
  const cash = portfolio?.cash || 0;
  const pnl = portfolio?.pnl || {};

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
        Portfolio
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Card sx={{ bgcolor: '#131b3a' }}>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Total Value
              </Typography>
              <Typography variant="h4" sx={{ color: '#00d4ff' }}>
                ${totalValue.toLocaleString()}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card sx={{ bgcolor: '#131b3a' }}>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Cash Balance
              </Typography>
              <Typography variant="h4" sx={{ color: '#4caf50' }}>
                ${cash.toLocaleString()}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card sx={{ bgcolor: '#131b3a' }}>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Total P&L
              </Typography>
              <Typography
                variant="h4"
                sx={{ color: pnl.total_pnl >= 0 ? '#4caf50' : '#f44336' }}
              >
                ${pnl.total_pnl?.toLocaleString() || '0'}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Return: {pnl.return_pct?.toFixed(2) || 0}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {pieData.length > 0 && (
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3, bgcolor: '#131b3a' }}>
              <Typography variant="h6" gutterBottom>
                Position Allocation
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={(entry) => entry.name}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>
        )}

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, bgcolor: '#131b3a' }}>
            <Typography variant="h6" gutterBottom>
              P&L Breakdown
            </Typography>
            <Box sx={{ mt: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                <Typography>Realized P&L:</Typography>
                <Typography sx={{ color: pnl.realized_pnl >= 0 ? '#4caf50' : '#f44336' }}>
                  ${pnl.realized_pnl?.toFixed(2) || '0.00'}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                <Typography>Unrealized P&L:</Typography>
                <Typography sx={{ color: pnl.unrealized_pnl >= 0 ? '#4caf50' : '#f44336' }}>
                  ${pnl.unrealized_pnl?.toFixed(2) || '0.00'}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="h6">Total P&L:</Typography>
                <Typography
                  variant="h6"
                  sx={{ color: pnl.total_pnl >= 0 ? '#4caf50' : '#f44336' }}
                >
                  ${pnl.total_pnl?.toFixed(2) || '0.00'}
                </Typography>
              </Box>
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ bgcolor: '#131b3a' }}>
            <Box sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Open Positions
              </Typography>
            </Box>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Symbol</TableCell>
                    <TableCell align="right">Quantity</TableCell>
                    <TableCell align="right">Entry Price</TableCell>
                    <TableCell align="right">Current Price</TableCell>
                    <TableCell align="right">Unrealized P&L</TableCell>
                    <TableCell align="right">Realized P&L</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {positions.length > 0 ? (
                    positions.map((position) => (
                      <TableRow key={position.id}>
                        <TableCell>{position.symbol}</TableCell>
                        <TableCell align="right">{position.quantity}</TableCell>
                        <TableCell align="right">${position.entry_price?.toFixed(2)}</TableCell>
                        <TableCell align="right">
                          ${(position.current_price || position.entry_price)?.toFixed(2)}
                        </TableCell>
                        <TableCell
                          align="right"
                          sx={{ color: position.unrealized_pnl >= 0 ? '#4caf50' : '#f44336' }}
                        >
                          ${position.unrealized_pnl?.toFixed(2)}
                        </TableCell>
                        <TableCell
                          align="right"
                          sx={{ color: position.realized_pnl >= 0 ? '#4caf50' : '#f44336' }}
                        >
                          ${position.realized_pnl?.toFixed(2)}
                        </TableCell>
                      </TableRow>
                    ))
                  ) : (
                    <TableRow>
                      <TableCell colSpan={6} align="center">
                        No open positions
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
