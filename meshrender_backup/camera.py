"""A virtual camera in a 3D scene.
"""
import numpy as np
from perception import CameraIntrinsics

from .constants import Z_NEAR, Z_FAR

class VirtualCamera(object):
    """A virtual camera, including its intrinsics and its pose.

    Attributes
    ----------
    intrinsics : :obj:`percetion.CameraIntrinsics`
        The intrinsic properties of the camera, from the Berkeley AUTOLab's perception module.
    pose : (4,4) float
        A transform from camera to world coordinates that indicates
        the camera's pose. The camera frame's x axis points right,
        its y axis points down, and its z axis points towards
        the scene (i.e. standard OpenCV coordinates).
    z_near : float
        The near-plane clipping distance.
    z_far : float
        The far-plane clipping distance.
    """

    def __init__(self, intrinsics, pose=None, z_near=Z_NEAR, z_far=Z_FAR):
        """Initialize a virtual camera with the given intrinsics and initial pose in the world.

        Parameters
        ----------
        """
        if not isinstance(intrinsics, CameraIntrinsics):
            raise ValueError('intrinsics must be an object of type CameraIntrinsics')

        self.intrinsics = intrinsics
        self.pose = pose
        self.z_near = z_near
        self.z_far = z_far

    @property
    def V(self):
        """(4,4) float: A homogenous rigid transform matrix mapping world coordinates
        to camera coordinates. Equivalent to the OpenGL View matrix.

        Note that the OpenGL camera coordinate system has x to the right, y up, and z away
        from the scene towards the eye!
        """
        # Create inverse V (map from camera to world)
        V_inv = self.pose.copy()
        V_inv[:3,1:3] *= -1 # Reverse Y and Z axes

        # Compute V (map from world to camera
        V = np.linalg.inv(V_inv_GL)
        return V

    @property
    def P(self):
        """(4,4) float: A homogenous projective matrix for the camera, equivalent
        to the OpenGL Projection matrix.
        """
        P = np.zeros((4,4))
        P[0][0] = 2.0 * self.intrinsics.fx / self.intrinsics.width
        P[1][1] = 2.0 * self.intrinsics.fy / self.intrinsics.height
        P[0][2] = 1.0 - 2.0 * self.intrinsics.cx / self.intrinsics.width
        P[1][2] = 2.0 * self.intrinsics.cy / self.intrinsics.height - 1.0
        P[2][2] = -(self.z_far + self.z_near) / (self.z_far - self.z_near)
        P[3][2] = -1.0
        P[2][3] = -(2.0 * self.z_far * self.z_near) / (self.z_far - self.z_near)
        return P


    def resize(self, new_width, new_height):
        """Reset the camera intrinsics for a new width and height viewing window.

        Parameters
        ----------
        new_width : int
            The new window width, in pixels.
        new_height : int
            The new window height, in pixels.
        """
        # Compute X and Y scaling
        x_scale = float(new_width) / self.intrinsics.width
        y_scale = float(new_height) / self.intrinsics.height

        # Compute new intrinsics parameters
        center_x = float(self.intrinsics.width-1)/2
        center_y = float(self.intrinsics.height-1)/2
        orig_cx_diff = self.intrinsics.cx - center_x
        orig_cy_diff = self.intrinsics.cy - center_y
        scaled_center_x = float(new_width-1) / 2
        scaled_center_y = float(new_height-1) / 2
        cx = scaled_center_x + x_scale * orig_cx_diff
        cy = scaled_center_y + y_scale * orig_cy_diff
        fx = self.intrinsics.fx * x_scale
        fy = self.intrinsics.fy * x_scale

        # Create new intrinsics
        scaled_intrinsics = CameraIntrinsics(frame=self.intrinsics.frame,
                                             fx=fx, fy=fy, skew=self.intrinsics.skew,
                                             cx=cx, cy=cy, height=new_height, width=new_width)
        self.intrinsics = scaled_intrinsics