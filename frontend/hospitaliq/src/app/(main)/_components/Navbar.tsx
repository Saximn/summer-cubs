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
import InboxIcon from '@mui/icons-material/MoveToInbox';
import MailIcon from '@mui/icons-material/Mail';

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
  justifyContent: 'flex-end',
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

export default function Navbar() {
  const theme = useTheme();
  const [open, setOpen] = React.useState(false);

  const handleDrawerOpen = () => {
    setOpen(true);
  };

  const handleDrawerClose = () => {
    setOpen(false);
  };

  return (
      <Drawer variant="permanent" open={open}>
          <DrawerHeader>
              <IconButton onClick={open ? handleDrawerClose : handleDrawerOpen}>
                  {open ? <ChevronLeftIcon /> : <ChevronRightIcon />}
              </IconButton>
          </DrawerHeader>
          <Divider />
          <List>
              {['Dashboard', 'Simulation', 'Policy & Data Insight', 'Patient Allocation', 'Feedback Form'].map((text, index) => (
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
                              {index % 2 === 0 ? <InboxIcon /> : <MailIcon />}
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
                              ]}
                          />
                      </ListItemButton>
                  </ListItem>
              ))}
          </List>
      </Drawer>
  );
}