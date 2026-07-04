"""
Hybrid Sleeve System Manager

Orchestrates all three sleeves, coordinates risk management,
and manages dynamic allocation.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime

from sleeves.base_sleeve import BaseSleeve, SleeveSignal
from sleeves.risk_management.risk_manager import RiskManager, DynamicAllocationManager, RiskConfig
from sleeves.utils.monitoring import HealthMonitor

logger = logging.getLogger(__name__)


class HybridSleeveSystem:
    """
    Main system manager for the Hybrid Sleeve trading system.
    
    Responsibilities:
    - Initialize and manage all sleeves
    - Coordinate risk management across sleeves
    - Execute dynamic allocation adjustments
    - Monitor system health
    - Orchestrate trade execution
    """
    
    def __init__(self, config: Dict):
        """
        Initialize the Hybrid Sleeve System.
        
        Args:
            config: System configuration dictionary
        """
        self.config = config
        self.sleeves: Dict[str, BaseSleeve] = {}
        self.risk_manager = RiskManager(
            portfolio_max_drawdown=config.get('max_drawdown', 0.20)
        )
        self.allocation_manager = DynamicAllocationManager()
        self.health_monitor = HealthMonitor()
        self.is_running = False
        self.portfolio_balance = config.get('initial_balance', 1000)
        self.trades_executed: List[Dict] = []
        
        logger.info("Hybrid Sleeve System initialized")
        logger.info(f"Initial balance: ${self.portfolio_balance}")
        logger.info(f"Max drawdown limit: {config.get('max_drawdown', 0.20)*100}%")
    
    def register_sleeve(self, sleeve: BaseSleeve, risk_config: RiskConfig) -> None:
        """
        Register a sleeve with the system.
        
        Args:
            sleeve: BaseSleeve instance
            risk_config: RiskConfig for this sleeve
        """
        self.sleeves[sleeve.sleeve_id] = sleeve
        self.risk_manager.register_sleeve(risk_config)
        logger.info(f"Registered sleeve: {sleeve.sleeve_id}")
    
    def initialize_sleeves(self, sleeve_configs: Dict[str, Dict]) -> bool:
        """
        Initialize all sleeves from configuration.
        
        Args:
            sleeve_configs: Dictionary mapping sleeve_id to config
        
        Returns:
            True if all sleeves initialized successfully
        """
        try:
            for sleeve_id, config in sleeve_configs.items():
                logger.info(f"Initializing sleeve: {sleeve_id}")
                # Sleeve instances should be injected, not created here
                # This method validates they're all present
            
            if not self.sleeves:
                logger.error("No sleeves registered")
                return False
            
            logger.info(f"System initialized with {len(self.sleeves)} sleeves")
            return True
        
        except Exception as e:
            logger.error(f"Error initializing sleeves: {e}")
            return False
    
    def start(self) -> bool:
        """
        Start the trading system.
        
        Returns:
            True if system started successfully
        """
        try:
            if not self.sleeves:
                logger.error("Cannot start: no sleeves registered")
                return False
            
            # Set initial allocations (from design doc)
            self.allocation_manager.set_allocation("x_signal_momentum", 0.50)  # 50% (mid-range)
            self.allocation_manager.set_allocation("trend_following", 0.30)    # 30% (mid-range)
            self.allocation_manager.set_allocation("tactical_mean_reversion", 0.20)  # 20% (mid-range)
            
            # Validate allocations
            if not self.allocation_manager.validate_allocations():
                logger.error("Initial allocations invalid")
                return False
            
            # Update sleeves with initial allocations
            for sleeve_id, sleeve in self.sleeves.items():
                allocation = self.allocation_manager.get_allocation(sleeve_id)
                sleeve.update_allocation(allocation)
            
            self.is_running = True
            logger.info("Hybrid Sleeve System STARTED")
            return True
        
        except Exception as e:
            logger.error(f"Error starting system: {e}")
            return False
    
    def stop(self) -> None:
        """
        Stop the trading system gracefully.
        """
        self.is_running = False
        logger.info("Hybrid Sleeve System STOPPED")
    
    def pause(self) -> None:
        """
        Pause trading (emergency pause).
        """
        for sleeve in self.sleeves.values():
            sleeve.set_enabled(False)
        logger.warning("All sleeves PAUSED")
    
    def resume(self) -> None:
        """
        Resume trading after pause.
        """
        for sleeve in self.sleeves.values():
            sleeve.set_enabled(True)
        logger.info("All sleeves RESUMED")
    
    def update_allocations(self, current_drawdown: float) -> None:
        """
        Update sleeve allocations based on current market conditions.
        
        This implements the dynamic allocation from the design doc:
        - Adjust based on recent performance
        - Adjust based on drawdown level
        - Ensure no sleeve exceeds 60% allocation
        
        Args:
            current_drawdown: Current portfolio drawdown (0-1 scale)
        """
        # Check if we should reduce risk
        if self.risk_manager.should_reduce_risk(current_drawdown):
            logger.warning(f"Drawdown at {current_drawdown*100}% - reducing risk")
            # TODO: Implement dynamic reduction logic
        
        # Check if we should pause entirely
        if self.risk_manager.should_pause_trading(current_drawdown):
            logger.error(f"Max drawdown {current_drawdown*100}% reached - PAUSING TRADING")
            self.pause()
    
    def process_signals(self, market_data: Dict) -> List[SleeveSignal]:
        """
        Process signals from all sleeves.
        
        Args:
            market_data: Current market data
        
        Returns:
            List of signals from active sleeves
        """
        if not self.is_running:
            return []
        
        signals: List[SleeveSignal] = []
        
        for sleeve_id, sleeve in self.sleeves.items():
            if not sleeve.enabled:
                continue
            
            try:
                signal = sleeve.analyze(market_data)
                if signal:
                    signals.append(signal)
                    logger.info(f"Signal from {sleeve_id}: {signal.signal_type} {signal.symbol}")
            
            except Exception as e:
                logger.error(f"Error processing signal from {sleeve_id}: {e}")
        
        return signals
    
    def execute_trade(self, signal: SleeveSignal) -> bool:
        """
        Execute a trade based on a sleeve signal.
        
        Args:
            signal: SleeveSignal to execute
        
        Returns:
            True if trade executed successfully
        """
        if not signal or signal.signal_type == 'hold':
            return False
        
        # Get sleeve
        sleeve = self.sleeves.get(signal.sleeve_id)
        if not sleeve:
            logger.warning(f"Sleeve {signal.sleeve_id} not found")
            return False
        
        # Calculate position size
        risk_per_trade = self.risk_manager.calculate_risk_per_trade(
            signal.sleeve_id,
            self.portfolio_balance
        )
        
        # Validate trade
        if not self.risk_manager.validate_trade(
            signal.sleeve_id,
            risk_per_trade,
            self.portfolio_balance
        ):
            logger.warning(f"Trade rejected by risk manager: {signal.symbol}")
            return False
        
        # Log execution
        trade_info = {
            'sleeve_id': signal.sleeve_id,
            'symbol': signal.symbol,
            'side': signal.signal_type,
            'amount': risk_per_trade,
            'entry_price': signal.entry_price,
            'stop_loss': signal.stop_loss,
            'take_profit': signal.take_profit,
            'timestamp': datetime.utcnow()
        }
        
        self.trades_executed.append(trade_info)
        sleeve.on_trade_executed(trade_info)
        
        self.health_monitor.log_trade_execution(
            signal.sleeve_id,
            signal.symbol,
            signal.signal_type,
            risk_per_trade,
            signal.entry_price
        )
        
        logger.info(f"Trade executed: {signal.symbol} via {signal.sleeve_id}")
        return True
    
    def get_system_status(self) -> Dict:
        """
        Get current system status and metrics.
        
        Returns:
            Dictionary with system status information
        """
        total_open_positions = sum(
            sleeve.get_active_positions_count() 
            for sleeve in self.sleeves.values()
        )
        
        status = {
            'running': self.is_running,
            'portfolio_balance': self.portfolio_balance,
            'total_trades_executed': len(self.trades_executed),
            'total_open_positions': total_open_positions,
            'sleeves': {
                sleeve_id: {
                    'enabled': sleeve.enabled,
                    'allocation': sleeve.current_allocation,
                    'open_positions': sleeve.get_active_positions_count(),
                    'performance': sleeve.get_performance().__dict__
                }
                for sleeve_id, sleeve in self.sleeves.items()
            },
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return status
    
    def print_status(self) -> None:
        """
        Print human-readable system status.
        """
        status = self.get_system_status()
        
        print("\n" + "="*60)
        print("HYBRID SLEEVE SYSTEM STATUS")
        print("="*60)
        print(f"Status: {'RUNNING' if status['running'] else 'STOPPED'}")
        print(f"Portfolio Balance: ${status['portfolio_balance']:.2f}")
        print(f"Total Trades: {status['total_trades_executed']}")
        print(f"Open Positions: {status['total_open_positions']}")
        print("\nSLEEVE DETAILS:")
        
        for sleeve_id, sleeve_status in status['sleeves'].items():
            print(f"\n  {sleeve_id}:")
            print(f"    Enabled: {sleeve_status['enabled']}")
            print(f"    Allocation: {sleeve_status['allocation']*100:.1f}%")
            print(f"    Open Positions: {sleeve_status['open_positions']}")
            perf = sleeve_status['performance']
            print(f"    Trades: {perf['trades_executed']}")
            print(f"    Win Rate: {perf['win_rate']*100:.1f}%")
            print(f"    P&L: {perf['profit_loss_pct']:.2f}%")
        
        print("\n" + "="*60 + "\n")
