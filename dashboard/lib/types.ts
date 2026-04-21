export interface StatusData {
  regime: string | null;
  strategy: string | null;
  pair: string | null;
  signal_score: number | null;
  last_heartbeat: string | null;
  is_running: boolean;
  is_paused: boolean;
  uptime_seconds: number;
}

export interface PnLPoint {
  timestamp: string;
  equity: number;
}

export interface PnLData {
  equity_curve: PnLPoint[];
  sharpe: number;
  max_drawdown: number;
  win_rate: number;
  total_pnl: number;
}

export interface Position {
  id: number;
  pair: string;
  direction: 'long' | 'short';
  entry_price: number;
  position_size: number;
  stop_loss: number;
  take_profit: number;
  trailing_stop_high: number | null;
  opened_at: string;
  order_id: string | null;
  outcome: string | null;
  is_open: number;
}

export interface SignalItem {
  pair: string;
  rsi: number | null;
  macd: number | null;
  vwap: number | null;
  bb: number | null;
  sentiment: number | null;
  composite: number | null;
  timestamp: string | null;
}

export interface Trade {
  id: number;
  timestamp: string;
  pair: string;
  regime: string;
  strategy: string;
  action: string;
  signal_score: number;
  entry_price: number | null;
  position_size: number | null;
  stop_loss: number | null;
  take_profit: number | null;
  outcome: string | null;
}

export interface TradesData {
  items: Trade[];
  total: number;
  page: number;
  pages: number;
}

export type WsEvent =
  | { type: 'trade_executed'; data: Trade }
  | { type: 'signal_changed'; data: SignalItem[] }
  | { type: 'regime_changed'; data: { regime: string } }
  | { type: 'circuit_breaker_triggered'; data: { is_paused: boolean } };
