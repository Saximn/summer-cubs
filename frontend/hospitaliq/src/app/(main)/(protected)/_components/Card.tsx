'use client';
import { Box, Slider } from "@mui/material"

interface CardProps extends React.PropsWithChildren<{}> {
  className?: string;
  color?: string;
}

const marks = [
  {
    value: 0,
    label: '0',
  },
  {
    value: 1,
    label: '',
  },
  {
    value: 2,
    label: '2',
  },
  {
    value: 3,
    label: '',
  },
  {
    value: 4,
    label: '4',
  },
  {
    value: 5,
    label: '',
  },
  {
    value: 6,
    label: '6',
  },
  {
    value: 7,
    label: '',
  },
  {
    value: 8,
    label: '8',
  },
  {
    value: 9,
    label: '',
  },
  {
    value: 10,
    label: '10',
  },
];

function valuetext(value: number) {
  return `${value}`;
}

const DiscreteSliderLabel = () => (
  <Slider
      aria-label="Always visible"
      defaultValue={5}
      getAriaValueText={valuetext}
      step={1}
      marks={marks}
      valueLabelDisplay="on"
      min={0}
      max={10}
      sx={{
      color: 'navy',
      '& .MuiSlider-markLabel': {
        fontWeight: 'bold', 
        fontSize: 15, 
        color: 'gray'
      },
      '& .MuiSlider-thumb': {
        backgroundColor: 'white',
        border: '1px solid navy',
      },
      }}
  />
)


const Card: React.FC<CardProps>= ({children, className, color}) => (
  <>
    <Box
      className={className}
      sx={{
      backgroundColor: color,
      borderRadius: '10px',
      padding: '16px',
      boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
      height: '100%',
      width: '100%',
      }}
    >
      <Box sx={{ marginBottom: '40px' }}>{children}</Box>
      {className === 'flex flex-col gap-3 min-w-[300px]' ?<DiscreteSliderLabel/> : null }
    </Box>
  </>
)

export default Card;