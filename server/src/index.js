const express = require('express');
const path = require('path');

const connectionsRouter = require('./connections');
const connectionsReportRouter = require('./connectionsReport');

const spellingbeeRouter = require('./spellingbee').router;
const spellingbeeReportRouter = require('./spellingbeeReport');

const PUBLIC_DIR = path.join(__dirname, '../public');
const CONNECTIONS_DIR = path.join(PUBLIC_DIR, 'connections');
const SPELLINGBEE_DIR = path.join(PUBLIC_DIR, 'spellingbee');

const app = express();
app.use(express.json());

app.use('/api/connections/report', connectionsReportRouter);
app.use('/api/connections', connectionsRouter);

app.use('/connections', express.static(CONNECTIONS_DIR));
app.get('/connections', (req, res) => {
    res.sendFile(path.join(CONNECTIONS_DIR, 'index.html'));
});

app.use('/api/spellingbee/report', spellingbeeReportRouter);
app.use('/api/spellingbee', spellingbeeRouter);

app.use('/spellingbee', express.static(SPELLINGBEE_DIR));
app.get('/spellingbee', (req, res) => {
    res.sendFile(path.join(SPELLINGBEE_DIR, 'index.html'));
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});