import { Box, TextField, Button } from "@mui/material"
import Card from '../_components/Card';

export default function FeedbackPage() {
  return (
    <Box className="bg-primary rounded flex items-center justify-center h-[530px] w-[530px] p-9 ">
      <Box className="flex flex-col items-start justify-start w-full h-full">
        <h4 className="font-bold text-3xl text-white mb-4">Feedback</h4>
        <Card className="h-80" color="white">
          <Box
            component="form"
            sx={{ '& .MuiTextField-root': { width: '400px' } }}
            noValidate
            autoComplete="off"
          >
            <div>
              <TextField
                id="standard-multiline-static"
                label="Add feedback!"
                multiline
                rows={11}
                variant="standard"
                />
            </div>
          </Box>
        </Card>
        <Button className="top-10 bg-background rounded-full font-bold text-xs p-3 w-42 ml-38" variant="contained">Submit</Button>
       </Box>
    </Box>
  )
}