const express = require('express');
const path = require('path');

const connectionsRouter = require('./connections');
const connectionsReportRouter = require('./connectionsReport');

const spellingbeeRouter = require('./spellingbee').router;
const spellingbeeReportRouter = require('./spellingbeeReport');

const PUBLIC_DIR = path.join(__dirname, '../public');
const CONNECTIONS_INDEX = path.join(PUBLIC_DIR, 'connections', 'index.html');
const SPELLINGBEE_INDEX = path.join(PUBLIC_DIR, 'spellingbee', 'index.html');

const app = express();
app.use(express.json());

app.use('/api/connections/report', connectionsReportRouter);
app.use('/api/connections', connectionsRouter);

app.get('/connections', (req, res) => {
    res.sendFile(CONNECTIONS_INDEX);
});

app.use('/api/spellingbee/report', spellingbeeReportRouter);
app.use('/api/spellingbee', spellingbeeRouter);

app.get('/spellingbee', (req, res) => {
    res.sendFile(SPELLINGBEE_INDEX);
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});