"""
∇C - Chemotropic Navigation Accuracy

Measures the directional precision with which growing hyphal tips navigate
toward resource targets through detection and response to chemical concentration
gradients.

Physical mechanism: Differential growth rates across hyphal tip in response
to asymmetric receptor activation, translating spatial chemical gradients
into directional growth vectors.

Units: Angular deviation from optimal trajectory (degrees) or normalized accuracy
Reference range: 0.78 - 0.96 normalized (0°-12° deviation)
"""

import numpy as np
from typing import Dict, Optional, Union, Tuple, List
from dataclasses import dataclass


@dataclass
class TrajectoryPoint:
    """Represents a single point in hyphal growth trajectory."""
    
    x: float  # μm
    y: float  # μm
    z: float  # μm (if 3D)
    t: float  # seconds
    confidence: float  # tracking confidence (0-1)


@dataclass
class GradientField:
    """Represents a chemical concentration gradient."""
    
    direction: Tuple[float, float, float]  # unit vector
    magnitude: float  # μM/μm
    chemical: str  # e.g., 'phosphate', 'ammonium', 'glucose'
    source_location: Tuple[float, float, float]


@dataclass
class GradCResult:
    """Container for ∇C calculation results."""
    
    value: float  # normalized navigation accuracy
    angular_error: float  # degrees
    trajectory_length: float  # μm
    n_points: int
    gradient_direction: Tuple[float, float, float]
    mean_deviation: float  # mean angular deviation (degrees)
    max_deviation: float  # maximum deviation (degrees)
    chemotactic_index: float  # 0-1, how strongly directed
    warnings: List[str] = None


class GradCCalculator:
    """
    Calculator for Chemotropic Navigation Accuracy (∇C).
    
    ∇C_norm = 1 - (θ_error / 180°)
    
    where θ_error is the angular deviation of actual hyphal growth
    trajectory from the true gradient direction ∇φ.
    
    θ_error = arccos( (v_actual · v_gradient) / (|v_actual|·|v_gradient|) )
    """
    
    def __init__(self):
        """Initialize ∇C calculator."""
        pass
    
    def load_trajectory(
        self,
        points: List[Tuple[float, float, float, float]]
    ) -> List[TrajectoryPoint]:
        """
        Load hyphal tip tracking data.
        
        Args:
            points: List of (x, y, z, t) tuples or (x, y, t) for 2D
        
        Returns:
            List of TrajectoryPoint objects
        """
        trajectory = []
        for i, point in enumerate(points):
            if len(point) == 4:
                x, y, z, t = point
                confidence = 0.95  # Default confidence
            elif len(point) == 3:
                x, y, t = point
                z = 0.0
                confidence = 0.9
            else:
                continue
            
            trajectory.append(TrajectoryPoint(
                x=x, y=y, z=z, t=t, confidence=confidence
            ))
        
        return trajectory
    
    def estimate_gradient(
        self,
        trajectory: List[TrajectoryPoint],
        chemical: str = 'phosphate'
    ) -> GradientField:
        """
        Estimate chemical gradient direction from trajectory.
        
        In real applications, this would use direct measurements from
        microsampling arrays. Here we estimate from trajectory if needed.
        """
        if len(trajectory) < 2:
            return GradientField(
                direction=(1.0, 0.0, 0.0),
                magnitude=0.0,
                chemical=chemical,
                source_location=(0, 0, 0)
            )
        
        # Use overall direction of movement as proxy for gradient
        start = trajectory[0]
        end = trajectory[-1]
        
        dx = end.x - start.x
        dy = end.y - start.y
        dz = end.z - start.z
        dist = np.sqrt(dx*dx + dy*dy + dz*dz)
        
        if dist > 0:
            direction = (dx/dist, dy/dist, dz/dist)
        else:
            direction = (1.0, 0.0, 0.0)
        
        return GradientField(
            direction=direction,
            magnitude=0.1,  # placeholder
            chemical=chemical,
            source_location=(end.x, end.y, end.z)
        )
    
    def compute_angular_error(
        self,
        trajectory: List[TrajectoryPoint],
        gradient: GradientField
    ) -> Tuple[float, float, List[float]]:
        """
        Compute angular deviation between growth and gradient.
        
        Returns:
            (mean_error, max_error, all_errors)
        """
        if len(trajectory) < 2:
            return 0.0, 0.0, []
        
        errors = []
        
        for i in range(1, len(trajectory)):
            # Growth direction at this segment
            p1 = trajectory[i-1]
            p2 = trajectory[i]
            
            dx = p2.x - p1.x
            dy = p2.y - p1.y
            dz = p2.z - p1.z
            dist = np.sqrt(dx*dx + dy*dy + dz*dz)
            
            if dist < 1e-6:
                continue
            
            growth_dir = (dx/dist, dy/dist, dz/dist)
            
            # Calculate angle between growth and gradient
            dot = (growth_dir[0]*gradient.direction[0] +
                   growth_dir[1]*gradient.direction[1] +
                   growth_dir[2]*gradient.direction[2])
            
            # Clamp to avoid numerical issues
            dot = max(-1.0, min(1.0, dot))
            
            angle_rad = np.arccos(dot)
            angle_deg = np.degrees(angle_rad)
            errors.append(angle_deg)
        
        if not errors:
            return 0.0, 0.0, []
        
        return np.mean(errors), np.max(errors), errors
    
    def compute_chemotactic_index(
        self,
        trajectory: List[TrajectoryPoint],
        gradient: GradientField
    ) -> float:
        """
        Compute chemotactic index (0-1) - how directed the growth is.
        
        CI = (distance_toward_source) / (total_path_length)
        """
        if len(trajectory) < 2:
            return 0.0
        
        # Calculate source direction
        start = trajectory[0]
        
        # Assume source is at gradient source location
        sx, sy, sz = gradient.source_location
        
        # Direction from start to source
        dx = sx - start.x
        dy = sy - start.y
        dz = sz - start.z
        dist_to_source = np.sqrt(dx*dx + dy*dy + dz*dz)
        
        if dist_to_source < 1e-6:
            return 1.0
        
        source_dir = (dx/dist_to_source, dy/dist_to_source, dz/dist_to_source)
        
        # Calculate net displacement toward source
        net_displacement = 0.0
        total_path = 0.0
        
        for i in range(1, len(trajectory)):
            p1 = trajectory[i-1]
            p2 = trajectory[i]
            
            # Path segment vector
            dx = p2.x - p1.x
            dy = p2.y - p1.y
            dz = p2.z - p1.z
            segment_length = np.sqrt(dx*dx + dy*dy + dz*dz)
            total_path += segment_length
            
            if segment_length > 0:
                # Project segment onto source direction
                segment_dir = (dx/segment_length, dy/segment_length, dz/segment_length)
                dot = (segment_dir[0]*source_dir[0] +
                       segment_dir[1]*source_dir[1] +
                       segment_dir[2]*source_dir[2])
                net_displacement += segment_length * max(0, dot)
        
        if total_path > 0:
            return net_displacement / total_path
        else:
            return 0.0
    
    def compute(
        self,
        trajectory_points: List[Tuple[float, float, float, float]],
        gradient: Optional[GradientField] = None,
        chemical: str = 'phosphate'
    ) -> GradCResult:
        """
        Compute ∇C from hyphal tip tracking data.
        
        Args:
            trajectory_points: List of (x, y, z, t) points
            gradient: Known gradient field (if None, estimated)
            chemical: Target chemical gradient
        
        Returns:
            GradCResult object with calculated value and metadata
        """
        # Load trajectory
        trajectory = self.load_trajectory(trajectory_points)
        
        if len(trajectory) < 2:
            return GradCResult(
                value=0.0,
                angular_error=90.0,
                trajectory_length=0.0,
                n_points=len(trajectory),
                gradient_direction=(0,0,0),
                mean_deviation=0,
                max_deviation=0,
                chemotactic_index=0,
                warnings=["Insufficient trajectory points"]
            )
        
        # Get or estimate gradient
        if gradient is None:
            gradient = self.estimate_gradient(trajectory, chemical)
        
        # Calculate trajectory length
        length = 0.0
        for i in range(1, len(trajectory)):
            p1 = trajectory[i-1]
            p2 = trajectory[i]
            dx = p2.x - p1.x
            dy = p2.y - p1.y
            dz = p2.z - p1.z
            length += np.sqrt(dx*dx + dy*dy + dz*dz)
        
        # Compute angular errors
        mean_error, max_error, all_errors = self.compute_angular_error(
            trajectory, gradient
        )
        
        # Compute chemotactic index
        chem_index = self.compute_chemotactic_index(trajectory, gradient)
        
        # Calculate normalized navigation accuracy
        # ∇C_norm = 1 - (mean_error / 180)
        # But typical range is 0-20 degrees, so we scale
        if mean_error < 20:
            # Excellent navigation (<20° error) maps to 0.89-1.0
            value = 1.0 - (mean_error / 180)
        else:
            # Poor navigation maps to lower values
            value = max(0, 1.0 - (mean_error / 90))
        
        # Adjust based on chemotactic index
        value = value * (0.5 + 0.5 * chem_index)
        
        # Generate warnings
        warnings = []
        if value < 0.6:
            warnings.append("Poor chemotropic navigation - possible gradient disruption")
        elif value < 0.78:
            warnings.append("Reduced navigation accuracy")
        
        if chem_index < 0.3:
            warnings.append("Very weak chemotactic response")
        
        if mean_error > 30:
            warnings.append(f"Large navigation error ({mean_error:.1f}°)")
        
        return GradCResult(
            value=min(1.0, max(0.0, value)),
            angular_error=mean_error,
            trajectory_length=length,
            n_points=len(trajectory),
            gradient_direction=gradient.direction,
            mean_deviation=mean_error,
            max_deviation=max_error,
            chemotactic_index=chem_index,
            warnings=warnings
        )
    
    @staticmethod
    def simulate_trajectory(
        target_direction: Tuple[float, float, float] = (1, 0, 0),
        noise_level: float = 5.0,  # degrees
        length: int = 100,
        step_size: float = 10.0  # μm
    ) -> List[Tuple[float, float, float, float]]:
        """
        Simulate hyphal growth trajectory for testing.
        
        Args:
            target_direction: Preferred growth direction
            noise_level: Angular noise in degrees
            length: Number of steps
            step_size: Step size in μm
        
        Returns:
            List of (x, y, z, t) points
        """
        points = [(0.0, 0.0, 0.0, 0.0)]
        current_pos = np.array([0.0, 0.0, 0.0])
        target_dir = np.array(target_direction)
        target_dir = target_dir / np.linalg.norm(target_dir)
        
        for i in range(1, length):
            # Add noise to direction
            noise_rad = np.radians(np.random.normal(0, noise_level))
            
            # Create rotation matrix around random axis
            axis = np.random.randn(3)
            axis = axis / np.linalg.norm(axis)
            
            # Rodrigues rotation formula
            cos_theta = np.cos(noise_rad)
            sin_theta = np.sin(noise_rad)
            
            direction = (target_dir * cos_theta +
                        np.cross(axis, target_dir) * sin_theta +
                        axis * np.dot(axis, target_dir) * (1 - cos_theta))
            direction = direction / np.linalg.norm(direction)
            
            # Take step
            current_pos += direction * step_size
            
            points.append((
                current_pos[0],
                current_pos[1],
                current_pos[2],
                i * 60.0  # 1 minute per step
            ))
        
        return points


# Convenience function
def compute_grad_c(
    trajectory_points: List[Tuple[float, float, float, float]],
    **kwargs
) -> float:
    """
    Convenience function to compute ∇C.
    
    Args:
        trajectory_points: List of (x, y, z, t) points
        **kwargs: Additional parameters for GradCCalculator.compute()
    
    Returns:
        Normalized navigation accuracy
    """
    calculator = GradCCalculator()
    result = calculator.compute(trajectory_points, **kwargs)
    return result.value
