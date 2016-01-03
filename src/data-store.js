import Sequelize from 'sequelize';

function defineDraftItem(sequelize) {
    return sequelize.define('draftitem', {
        id: {
            type: Sequelize.INTEGER,
            primaryKey: true,
            autoIncrement: true
        },
        item_type: {
            type: Sequelize.CHAR(1),
            allowNull: false
        },
        body: {
            type: Sequelize.TEXT,
            allowNull: false
        }
    }, {
        timestamps: true,
        underscored: true
    });
}

class DataStore {
    constructor() {
        var sequelize = new Sequelize('teoremer', null, null, {
          dialect: 'sqlite',
          storage: './db.sqlite'
        });
        this.DraftItem = defineDraftItem(sequelize);
    }
    static get DEFINITION() {
        return 'D';
    }
    init() {
        return this.DraftItem.sync();
    }
    create_draft(item_type, body) {
        return this.DraftItem.create({
            item_type: item_type,
            body: body
        }).then(item => item.id);
    }
}

var datastore = new DataStore();

datastore.init().then(() => {
    console.log('init ok');
    return datastore.create_draft(DataStore.DEFINITION, 'Hula bula');
}).then(id =>
    console.log('create ok', id)
).catch(() => {
    console.log('db fail');
});
