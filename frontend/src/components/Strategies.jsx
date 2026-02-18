import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import PauseIcon from '@mui/icons-material/Pause';
import axios from 'axios';

export default function Strategies() {
  const [strategies, setStrategies] = useState([]);
  const [openDialog, setOpenDialog] = useState(false);
  const [newStrategy, setNewStrategy] = useState({
    name: '',
    description: '',
    strategy_type: 'momentum',
    parameters: {},
  });

  useEffect(() => {
    fetchStrategies();
  }, []);

  const fetchStrategies = async () => {
    try {
      const response = await axios.get('/api/strategies');
      setStrategies(response.data);
    } catch (error) {
      console.error('Error fetching strategies:', error);
    }
  };

  const handleCreateStrategy = async () => {
    try {
      await axios.post('/api/strategies', newStrategy);
      setOpenDialog(false);
      setNewStrategy({
        name: '',
        description: '',
        strategy_type: 'momentum',
        parameters: {},
      });
      fetchStrategies();
    } catch (error) {
      console.error('Error creating strategy:', error);
    }
  };

  const handleToggleStrategy = async (strategyId, isActive) => {
    try {
      const endpoint = isActive
        ? `/api/strategies/${strategyId}/deactivate`
        : `/api/strategies/${strategyId}/activate`;
      await axios.post(endpoint);
      fetchStrategies();
    } catch (error) {
      console.error('Error toggling strategy:', error);
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Trading Strategies</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setOpenDialog(true)}
        >
          Create Strategy
        </Button>
      </Box>

      <Grid container spacing={3}>
        {strategies.map((strategy) => (
          <Grid item xs={12} md={6} lg={4} key={strategy.id}>
            <Card sx={{ bgcolor: '#131b3a', height: '100%' }}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                  <Typography variant="h6">{strategy.name}</Typography>
                  <Chip
                    label={strategy.is_active ? 'Active' : 'Inactive'}
                    color={strategy.is_active ? 'success' : 'default'}
                    size="small"
                  />
                </Box>
                <Typography color="text.secondary" variant="body2" sx={{ mb: 2 }}>
                  {strategy.description || 'No description'}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Type: {strategy.strategy_type}
                </Typography>
                <Box sx={{ mt: 2 }}>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">
                        Total P&L
                      </Typography>
                      <Typography
                        variant="h6"
                        sx={{
                          color: strategy.total_pnl >= 0 ? '#4caf50' : '#f44336',
                        }}
                      >
                        ${strategy.total_pnl?.toFixed(2) || '0.00'}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">
                        Win Rate
                      </Typography>
                      <Typography variant="h6">
                        {(strategy.win_rate * 100 || 0).toFixed(1)}%
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">
                        Sharpe Ratio
                      </Typography>
                      <Typography variant="h6">
                        {strategy.sharpe_ratio?.toFixed(2) || '0.00'}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">
                        Max Drawdown
                      </Typography>
                      <Typography variant="h6">
                        {(strategy.max_drawdown * 100 || 0).toFixed(1)}%
                      </Typography>
                    </Grid>
                  </Grid>
                </Box>
              </CardContent>
              <CardActions>
                <Button
                  size="small"
                  startIcon={strategy.is_active ? <PauseIcon /> : <PlayArrowIcon />}
                  onClick={() => handleToggleStrategy(strategy.id, strategy.is_active)}
                  color={strategy.is_active ? 'warning' : 'success'}
                >
                  {strategy.is_active ? 'Pause' : 'Activate'}
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Strategy</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Strategy Name"
            value={newStrategy.name}
            onChange={(e) => setNewStrategy({ ...newStrategy, name: e.target.value })}
            margin="normal"
          />
          <TextField
            fullWidth
            label="Description"
            value={newStrategy.description}
            onChange={(e) => setNewStrategy({ ...newStrategy, description: e.target.value })}
            margin="normal"
            multiline
            rows={3}
          />
          <TextField
            fullWidth
            select
            label="Strategy Type"
            value={newStrategy.strategy_type}
            onChange={(e) => setNewStrategy({ ...newStrategy, strategy_type: e.target.value })}
            margin="normal"
          >
            <MenuItem value="momentum">Momentum</MenuItem>
            <MenuItem value="mean_reversion">Mean Reversion</MenuItem>
            <MenuItem value="ml_based">ML-Based</MenuItem>
            <MenuItem value="llm_powered">LLM-Powered</MenuItem>
            <MenuItem value="hybrid">Hybrid</MenuItem>
          </TextField>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button onClick={handleCreateStrategy} variant="contained">
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
