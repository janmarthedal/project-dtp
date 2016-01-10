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

export default class DataStore {
    constructor() {
        let sequelize = new Sequelize('teoremer', null, null, {
          dialect: 'sqlite',
          storage: './db.sqlite'
        });
        this.DraftItem = defineDraftItem(sequelize);
    }
    static get DEFINITION() {
        return 'D';
    }
    static get THEOREM() {
        return 'T';
    }
    static get PROOF() {
        return 'P';
    }
    init() {
        return Promise.all([
            this.DraftItem.sync(),
        ]);
    }
    create_draft(item_type, body) {
        return this.DraftItem.create({
            item_type,
            body
        }).then(item => item.id);
    }
}
