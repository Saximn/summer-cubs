"use client";

import React from 'react';
import { styled, useTheme, Theme, CSSObject } from '@mui/material/styles';
import MuiDrawer from '@mui/material/Drawer';
import List from '@mui/material/List';
import Divider from '@mui/material/Divider';
import IconButton from '@mui/material/IconButton';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import DashboardIcon from '@mui/icons-material/Dashboard';
import EngineeringIcon from '@mui/icons-material/Engineering';
import InsightsIcon from '@mui/icons-material/Insights';
import PersonalInjuryIcon from '@mui/icons-material/PersonalInjury';
import FeedbackIcon from '@mui/icons-material/Feedback';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import QuestionAnswerIcon from '@mui/icons-material/QuestionAnswer';
import { Box, Menu, MenuItem } from '@mui/material';
import { logoutAction } from '@/app/logout/actions';
import { getCurrentUser } from '@/lib/auth/getCurrentUser';

const drawerWidth = 260;

const openedMixin = (theme: Theme): CSSObject => ({
  width: drawerWidth,
  transition: theme.transitions.create('width', {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.enteringScreen,
  }),
  overflowX: 'hidden',
});

const closedMixin = (theme: Theme): CSSObject => ({
  transition: theme.transitions.create('width', {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  overflowX: 'hidden',
  width: `calc(${theme.spacing(7)} + 1px)`,
  [theme.breakpoints.up('sm')]: {
    width: `calc(${theme.spacing(8)} + 1px)`,
  },
});

const DrawerHeader = styled('div')(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: theme.spacing(0, 1),
  // necessary for content to be below app bar
  ...theme.mixins.toolbar,
}));


const Drawer = styled(MuiDrawer, { shouldForwardProp: (prop) => prop !== 'open' })(
  ({ theme }) => ({
    width: drawerWidth,
    flexShrink: 0,
    whiteSpace: 'nowrap',
    boxSizing: 'border-box',
    variants: [
      {
        props: ({ open }) => open,
        style: {
          ...openedMixin(theme),
          '& .MuiDrawer-paper': openedMixin(theme),
        },
      },
      {
        props: ({ open }) => !open,
        style: {
          ...closedMixin(theme),
          '& .MuiDrawer-paper': closedMixin(theme),
        },
      },
    ],
  }),
);

export default function Navbar({ user }: { user: any }) {
  const [open, setOpen] = React.useState(true);
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
  const accountMenuOpen = Boolean(anchorEl);
  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };
  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleDrawerOpen = () => {
    setOpen(true);
  };

  const handleDrawerClose = () => {
    setOpen(false);
  };

  const handleLogout = async () => {
    await logoutAction();
  };

  const NAVIGATION = [
    {
      text: 'Dashboard',
      icon: <DashboardIcon />,
      link: '/dashboard'
    },
    {
      text: 'Simulation',
      icon: <EngineeringIcon />,
      link: '/simulation'
    },
    {
      text: 'Policy & Data Insight',
      icon: <InsightsIcon />,
      link: '/policy'
    },
    {
      text: 'Patient Allocation',
      icon: <PersonalInjuryIcon />,
      link: '/patient'
    },
    {
      text: 'Feedback Form',
      icon: <FeedbackIcon />,
      link: '/feedback'
    },
    {
        text: 'Chatbot',
        icon: <QuestionAnswerIcon />,
        link: '/chatbot'
    },
  ]

  return (
    <Drawer variant="permanent" open={open}>
      <DrawerHeader>
        {open && (
          <img src="/logo-full.png" alt="HospitalIQ Logo" className='h-[80%]' />
        )}
        <IconButton onClick={open ? handleDrawerClose : handleDrawerOpen}>
          {open ? <ChevronLeftIcon /> : <ChevronRightIcon />}
        </IconButton>
      </DrawerHeader>
      <Divider />
      <List>
        {NAVIGATION.map(({ text, icon, link }) => (
          <ListItem className='px-2 py-1' key={text} disablePadding sx={{ display: 'block' }}>
            <ListItemButton
              className='bg-secondary hover:bg-secondary/50 rounded'
              sx={[
                {
                  minHeight: 60,
                },
                open
                  ? {
                    justifyContent: 'initial',
                  }
                  : {
                    justifyContent: 'center',
                  },
              ]}
              LinkComponent={'a'}
              href={link}
            >
              <ListItemIcon
                sx={[
                  {
                    minWidth: 0,
                    justifyContent: 'center',
                  },
                  open
                    ? {
                      mr: 3,
                    }
                    : {
                      mr: 'auto',
                    },
                ]}
              >
                {icon}
              </ListItemIcon>
              <ListItemText
                primary={text}
                sx={[
                  open
                    ? {
                      opacity: 1,
                    }
                    : {
                      opacity: 0,
                    },
                  {
                    '& .MuiTypography-root': {
                      fontWeight: 700
                    }
                  }
                ]}
              />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      <Box
        className="navbar-account"
        sx={{
          marginTop: 'auto',
          p: open ? 2 : 1,
          display: 'flex',
          alignItems: 'center',
          justifyContent: open ? 'flex-start' : 'center',
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
            marginRight: open ? 2 : 0,
            color: '#888'
          }}
        />
        {open && (
          <Box>
            <Box sx={{ fontWeight: 600 }}>{user?.fullname}</Box>
            <Box sx={{ fontSize: 12, color: '#888' }}>{user?.email}</Box>
          </Box>
        )}
      </Box>
      {/* Account Popup Menu */}
      <Box>
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
          <MenuItem onClick={() => {
            handleClose();
            handleLogout();
          }}>
            Logout
          </MenuItem>
        </Menu>
      </Box>
    </Drawer>
  );
}