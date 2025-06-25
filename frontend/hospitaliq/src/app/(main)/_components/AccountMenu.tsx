"use client";

import React from 'react';
import { Box, Menu, MenuItem } from '@mui/material';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import { logoutAction } from '@/app/logout/actions';

export default function AccountMenu({ user }: { user: any }) {
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
  const accountMenuOpen = Boolean(anchorEl);

  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = async () => {
    handleClose();
    await logoutAction();
  };

  return (
    <>
      <Box
        className="account-menu"
        sx={{
          p: 2,
          position: 'fixed',
          display: 'flex',
          height: 10,
          alignItems: 'center',
          justifyContent: 'flex-start',
          minHeight: 72,
          borderRadius: 2,
          cursor: 'pointer',
          transition: 'background 0.2s',
          '&:hover': {
            backgroundColor: '#f0f0f0',
          },
        }}
        onClick={handleClick}
      >
        <AccountCircleIcon
          sx={{
            width: 40,
            height: 40,
            borderRadius: '50%',
            marginRight: 2,
            color: '#888',
          }}
        />
        <Box>
          <Box sx={{ fontWeight: 600 }}>{user?.fullname}</Box>
          <Box sx={{ fontSize: 12, color: '#888' }}>{user?.email}</Box>
        </Box>
      </Box>

      <Menu
        anchorEl={anchorEl}
        open={accountMenuOpen}
        onClose={handleClose}
        anchorOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
      >
        <MenuItem onClick={handleLogout}>Logout</MenuItem>
      </Menu>
    </>
  );
}
